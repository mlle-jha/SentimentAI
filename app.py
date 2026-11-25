
"""
Minimal Flask API for the SentimentAI text-processing module.

Run with:
    python app.py

Text endpoint:
    POST /api/analyze
    JSON: {"text": "..."}

PDF endpoint:
    POST /api/analyze-pdf
    Multipart form field: file
"""

from pathlib import Path
from tempfile import NamedTemporaryFile

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from text_processor import analyze_pdf, analyze_text

# APPLICATION CONFIGURATION
BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "http://127.0.0.1:5500",
                "http://localhost:5500",
                "http://127.0.0.1:5000",
                "http://localhost:5000",
            ]
        }
    },
)

# Maximum PDF upload size: 15 MB
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024

# FRONTEND ROUTES
@app.get("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.get("/style.css")
def stylesheet():
    return send_from_directory(BASE_DIR, "style.css")


@app.get("/script.js")
def serve_script():
    return send_from_directory(BASE_DIR, "script.js")

# TEXT ANALYSIS API
@app.post("/api/analyze")
def analyze_manual_text():

    data = request.get_json(silent=True) or {}
    text = data.get("text", "")

    try:
        result = analyze_text(text)
        return jsonify(result)

    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400

# PDF ANALYSIS API
@app.post("/api/analyze-pdf")
def analyze_uploaded_pdf():

    uploaded_file = request.files.get("file")

    if uploaded_file is None or not uploaded_file.filename:
        return jsonify({
            "error": "Please select a PDF file."
        }), 400

    if not uploaded_file.filename.lower().endswith(".pdf"):
        return jsonify({
            "error": "Only PDF files are supported."
        }), 400

    temp_path = None

    try:
        with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            uploaded_file.save(temp_file)
            temp_path = Path(temp_file.name)

        result = analyze_pdf(temp_path)

        return jsonify(result)

    except (ValueError, FileNotFoundError) as error:
        return jsonify({"error": str(error)}), 400

    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()

# ERROR HANDLER
@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "error": "File is too large. Maximum upload size is 15 MB."
    }), 413

# RUN APPLICATION
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
