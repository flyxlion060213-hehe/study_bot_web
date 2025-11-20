from flask import Flask, request, jsonify, render_template
from google.genai import Client
import os, json

# ================= CONFIG =================
GEMINI_API_KEY = "đã điền"
client = Client(api_key=GEMINI_API_KEY)

app = Flask(__name__)

# ================= ROUTES =================

@app.route("/")
def home():
    return "Server is running!"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question")

    prompt = (
        "Bạn là trợ lý học tập thông minh, trả lời tiếng Việt rõ ràng.\n"
        f"Câu hỏi: {question}"
    )

    try:
        response = client.generate(
            model="gemini-2.0-flash",
            prompt=prompt,
        )
        answer = response.output_text
    except Exception as e:
        answer = f"⚠ Lỗi AI: {e}"

    return jsonify({"answer": answer})


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "Không có tệp!"}), 400

    f = request.files["file"]
    file_bytes = f.read()

    try:
        response = client.generate(
            model="gemini-2.0-flash",
            contents=[
                {"mime_type": f.mimetype, "data": file_bytes},
                {"text": "Hãy phân tích nội dung tệp này và trả lời tiếng Việt."}
            ]
        )
        answer = response.output_text
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=True)
