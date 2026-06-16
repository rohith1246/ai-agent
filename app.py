import os
import logging
from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
from dotenv import load_dotenv
from research_agent import research_agent, REPORTS_DIR

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

ALLOWED_DEPTHS = {"quick", "deep", "expert"}


@app.route('/logo.png')
def logo():
    return send_from_directory('.', 'logo.png')


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/research", methods=["POST"])
def research_route():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"success": False, "error": "Invalid request body."}), 400

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
            "success":    True,
            "filename":   result["filename"],
            "report":     result["report"],
            "sources":    result["sources"],
            "depth":      result["depth"],
            "model_used": result.get("model_used", "unknown"),
        })

    except RuntimeError as e:
        # Friendly errors raised intentionally by research_agent (e.g. all models rate-limited)
        logger.warning(f"Research failed (user-facing): {e}")
        return jsonify({"success": False, "error": str(e)}), 429

    except Exception as e:
        # Unexpected crash — log full traceback, return generic message
        logger.exception(f"Unexpected error in /research: {e}")
        return jsonify({"success": False, "error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route("/download/<filename>")
def download_report(filename):
    safe_name = os.path.basename(filename)
    filepath = os.path.join(REPORTS_DIR, safe_name)

    if not os.path.exists(filepath):
        return jsonify({"error": "Report not found."}), 404

    return send_file(filepath, as_attachment=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    app.run(debug=os.environ.get("FLASK_ENV") == "development", host="0.0.0.0", port=port)