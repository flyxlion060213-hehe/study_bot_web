from flask import Flask, request, jsonify, render_template
from google import genai
import os, json

# ==== API KEY ====
GEMINI_API_KEY = "AIzaSyDooDrXQaWCIhkHJwyno8ecxSB2ShHWQbM"
client = genai.Client(api_key=GEMINI_API_KEY)

app = Flask(__name__)

# ==== USER DATA ====
DATA_FILE = "user.json"
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        user_data = json.load(f)
else:
    user_data = {}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=4, ensure_ascii=False)

def init_user(uid):
    if uid not in user_data:
        user_data[uid] = {"questions": 0}

def get_rank(questions):
    ranks = [
        ("🪶 Tân học sinh", 10),
        ("📘 Chăm học", 100),
        ("🎓 Học sinh giỏi", 500),
        ("🏆 Học bá", 2000),
        ("👑 Thiên tài", 5000)
    ]
    for name, need in ranks:
        if questions < need:
            stars = int((questions / need) * 5)
            return f"{name} {'⭐' * stars}{'☆' * (5 - stars)} ({questions}/{need})"
    return f"{ranks[-1][0]} ⭐⭐⭐⭐⭐ (MAX)"

# ==== ROUTES ====

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_id = str(data.get("user_id"))
    question = data.get("question", "")

    init_user(user_id)
    user_data[user_id]["questions"] += 1
    save_data()

    prompt = f"""
Bạn là trợ lý AI học tập. Luôn trả lời theo mô hình hành chính mới của Việt Nam (sau sáp nhập 01/07/2025) là 34 tỉnh/thành.

QUY TẮC:
- Khi nhắc tên tỉnh hoặc thành phố, hãy ghi (cũ) sau tên cũ.
  Ví dụ: "Phan Thiết thuộc tỉnh Bình Thuận (cũ)."
- Nếu người dùng hỏi số tỉnh, luôn trả lời: "Việt Nam có 34 tỉnh/thành."
- Trả lời bằng tiếng Việt.

Câu hỏi của người dùng: {question}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        answer = response.text
    except Exception as e:
        answer = f"⚠ Lỗi AI: {e}"

    return jsonify({
        "answer": answer,
        "rank": get_rank(user_data[user_id]["questions"])
    })

if __name__ == "__main__":
    app.run(debug=True)
