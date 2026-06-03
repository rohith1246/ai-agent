from flask import Flask, request, jsonify, render_template, send_file
from dotenv import load_dotenv
import os

# Import functions from Day 5
from research_agent import search_web, write_report, save_report

load_dotenv()

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/research", methods=["POST"])
def research_route():

    data = request.get_json()
    topic = data.get("topic", "").strip()

    if not topic:
        return jsonify({
            "success": False,
            "error": "Please enter a topic."
        })

    print(f"Researching: {topic}")

    search_results = search_web(topic)

    report = write_report(
        topic,
        search_results
    )

    filename = save_report(
        topic,
        report
    )

    return jsonify({
        "success": True,
        "filename": filename,
        "preview": report[:500]
    })


@app.route("/download/<filename>")
def download_report(filename):
    return send_file(
        filename,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)