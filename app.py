from flask import Flask, request, render_template, jsonify
import google.generativeai as genai
import os, json, uuid

# ====== CẤU HÌNH ======
GEMINI_API_KEY = "AIzaSyDooDrXQaWCIhkHJwyno8ecxSB2ShHWQbM"
DATA_FILE = "user_data.json"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

app = Flask(__name__)

# ====== DỮ LIỆU NGƯỜI DÙNG ======
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            user_data = json.load(f)
        except:
            user_data = {}
else:
    user_data = {}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=4, ensure_ascii=False)

def init_user(user_id):
    uid = str(user_id)
    if uid not in user_data:
        user_data[uid] = {"questions": 0}
        save_data()

def get_rank(questions):
    ranks = [
        ("🪶 Tân học sinh", 10),
        ("📘 Chăm học", 100),
        ("🎓 Học sinh giỏi", 1000),
        ("🏆 Học bá", 10000),
        ("👑 Thiên tài", 100000)
    ]
    for name, need in ranks:
        if questions < need:
            stars = int((questions / need) * 5)
            return f"{name} {'⭐' * stars}{'☆' * (5 - stars)} ({questions}/{need})"
    return f"{ranks[-1][0]} ⭐⭐⭐⭐⭐ (MAX)"

# ====== ROUTES ======
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_id = data.get("user_id")
    question = data.get("question")

    if not user_id or not question:
        return jsonify({"error": "Missing parameters"}), 400

    init_user(user_id)
    user = user_data[str(user_id)]
    user["questions"] += 1
    save_data()

    prompt = (
        "Bạn là trợ lý học tập thông minh, luôn trả lời bằng tiếng Việt chuẩn. "
        f"Câu hỏi: {question}"
    )

    try:
        response = model.generate_content(prompt)
        answer = response.text
    except Exception as e:
        answer = f"⚠️ Lỗi khi gọi Gemini API: {e}"

    return jsonify({
        "answer": answer,
        "rank": get_rank(user["questions"])
    })

if __name__ == "__main__":
    app.run(debug=True)
