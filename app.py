from flask import Flask, request, jsonify, render_template
from google.genai import Client
import os, json

# Khởi tạo Client AI
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = Client(api_key=GEMINI_API_KEY)

app = Flask(__name__)

# ==== QUẢN LÝ DỮ LIỆU NGƯỜI DÙNG ====
DATA_FILE = "user.json"
user_data = {}

if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            user_data = json.load(f)
    except:
        user_data = {}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=4, ensure_ascii=False)

def get_rank(questions):
    ranks = [("🪶 Tân học sinh", 5), ("📘 Chăm học", 10), ("🎓 Học sinh giỏi", 20), ("🏆 Học bá", 50), ("👑 Thiên tài", 100)]
    for name, need in ranks:
        if questions < need:
            stars = int((questions / need) * 5)
            return f"{name} {'⭐' * stars}{'☆' * (5 - stars)}"
    return f"{ranks[-1][0]} ⭐⭐⭐⭐⭐"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_id = str(data.get("user_id", "guest"))
    question = data.get("question", "")

    if user_id not in user_data:
        user_data[user_id] = {"questions": 0}
    
    user_data[user_id]["questions"] += 1
    save_data()

    # LỆNH ÉP AI DÙNG IUPAC VÀ CẬP NHẬT HÀNH CHÍNH
    prompt = f"""
Bạn là trợ lý AI học tập. 
1. HÀNH CHÍNH: Trả lời theo mô hình 34 tỉnh/thành mới của VN (sau 01/07/2025).
2. HÓA HỌC: TUYỆT ĐỐI dùng danh pháp IUPAC tiếng Anh (Ví dụ: Aluminium, Iron(III) chloride, Sulfuric acid).
3. NGÔN NGỮ: Giải thích tiếng Việt.

Câu hỏi: {question}
"""

    try:
        # Sử dụng model Gemini 2.0 Flash mới nhất
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        answer = response.text
    except Exception as e:
        answer = f"⚠ Lỗi AI: {str(e)}"

    return jsonify({
        "answer": answer,
        "rank": get_rank(user_data[user_id]["questions"])
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
