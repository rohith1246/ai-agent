import os
import logging
from flask import Flask, request, jsonify, render_template, send_file
from dotenv import load_dotenv
from research_agent import research_agent, REPORTS_DIR

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/research", methods=["POST"])
def research_route():
    data = request.get_json()
    topic = data.get("topic", "").strip()

    if not topic:
        return jsonify({"success": False, "error": "Please enter a topic."})

    if len(topic) > 300:
        return jsonify({"success": False, "error": "Topic too long. Max 300 characters."})

    logger.info(f"Research request: {topic}")

    result = research_agent(topic)

    return jsonify({
        "success": True,
        "filename": result["filename"],
        "report": result["report"],
        "sources": result["sources"],
    })


@app.route("/download/<filename>")
def download_report(filename):
    # Sanitize: only allow files that exist in the reports directory
    safe_name = os.path.basename(filename)
    filepath = os.path.join(REPORTS_DIR, safe_name)

    if not os.path.exists(filepath):
        return jsonify({"error": "Report not found."}), 404

    return send_file(filepath, as_attachment=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=os.environ.get("FLASK_ENV") == "development", host="0.0.0.0", port=port)