import io
import os
import logging
from flask import Flask, request, jsonify, render_template, send_file
from dotenv import load_dotenv
from research_agent import research_agent, REPORTS_DIR
from pdf_generator import generate_pdf

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

ALLOWED_DEPTHS = {"quick", "deep", "expert"}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/research", methods=["POST"])
def research_route():
    data = request.get_json()
    topic = data.get("topic", "").strip()
    depth = data.get("depth", "quick").lower()

    if not topic:
        return jsonify({"success": False, "error": "Please enter a topic."})
    if len(topic) > 300:
        return jsonify({"success": False, "error": "Topic too long. Max 300 characters."})
    if depth not in ALLOWED_DEPTHS:
        depth = "quick"

    logger.info(f"Research request: {topic} [{depth}]")

    result = research_agent(topic, depth=depth)

    return jsonify({
        "success": True,
        "filename": result["filename"],
        "report": result["report"],
        "sources": result["sources"],
        "depth": result["depth"],
    })


@app.route("/download/<filename>")
def download_report(filename):
    safe_name = os.path.basename(filename)
    filepath = os.path.join(REPORTS_DIR, safe_name)

    if not os.path.exists(filepath):
        return jsonify({"error": "Report not found."}), 404

    return send_file(filepath, as_attachment=True)


@app.route("/download-pdf/<filename>")
def download_pdf(filename):
    safe_name = os.path.basename(filename)
    txt_path = os.path.join(REPORTS_DIR, safe_name)

    if not os.path.exists(txt_path):
        return jsonify({"error": "Report not found."}), 404

    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    topic = safe_name.replace("-report.txt", "").replace("-", " ").title()

    # Re-fetch sources isn't stored — pass empty list for now
    pdf_bytes = generate_pdf(topic, content, sources=[])
    pdf_filename = safe_name.replace(".txt", ".pdf")

    return send_file(
        io.BytesIO(pdf_bytes),
        as_attachment=True,
        download_name=pdf_filename,
        mimetype="application/pdf",
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=os.environ.get("FLASK_ENV") == "development", host="0.0.0.0", port=port)