from flask import Flask, request, jsonify, render_template
from google.genai import Client
import os, json

# ================= CONFIG =================
GEMINI_API_KEY = "AIzaSyDooDrXQaWCIhkHJwyno8ecxSB2ShHWQbM"
client = Client(api_key=GEMINI_API_KEY)

DATA_FILE = "user_data.json"

app = Flask(__name__)

# ================= USER DATA =================
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
        save_data()

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


# ================= ROUTES =================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question")
    user_id = str(data.get("user_id"))

    init_user(user_id)
    user_data[user_id]["questions"] += 1
    save_data()

    prompt = (
        "Bạn là trợ lý học tập, trả lời tiếng Việt rõ ràng.\n"
        f"Câu hỏi: {question}"
    )

    try:
        response = client.models.generate(
            model="gemini-2.0-flash",
            prompt=prompt,
        )
        answer = response.text
    except Exception as e:
        answer = f"⚠ Lỗi AI: {e}"

    return jsonify({
        "answer": answer,
        "rank": get_rank(user_data[user_id]["questions"])
    })


@app.route("/upload", methods=["POST"])
def upload():
    user_id = str(request.form.get("user_id"))
    init_user(user_id)
    user_data[user_id]["questions"] += 1
    save_data()

    if "file" not in request.files:
        return jsonify({"error": "Không có tệp!"}), 400

    f = request.files["file"]
    file_bytes = f.read()

    try:
        response = client.models.generate(
            model="gemini-2.0-flash",
            contents=[
                {"mime_type": f.mimetype, "data": file_bytes},
                {"text": "Hãy phân tích tài liệu này và trả lời tiếng Việt."}
            ]
        )
        answer = response.text
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "answer": answer,
        "rank": get_rank(user_data[user_id]["questions"])
    })


if __name__ == "__main__":
    app.run(debug=True)
