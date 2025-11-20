from flask import Flask, request, render_template, jsonify
import google.generativeai as genai

# ====== CẤU HÌNH ======
GEMINI_API_KEY = ""
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

app = Flask(__name__)

# ====== ROUTES ======
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question")

    if not question:
        return jsonify({"error": "Vui lòng nhập câu hỏi"}), 400

    prompt = (
        "Bạn là trợ lý học tập thông minh, luôn trả lời bằng tiếng Việt chuẩn. "
        f"Câu hỏi: {question}"
    )

    try:
        response = model.generate_content(prompt)
        answer = response.text
    except Exception as e:
        answer = f"⚠️ Lỗi khi gọi Gemini API: {e}"

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
