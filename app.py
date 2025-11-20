from flask import Flask, request, jsonify, render_template
import google.genai as genai
import os, json

# ================= CONFIG =================
GEMINI_API_KEY = "AIzaSyDooDrXQaWCIhkHJwyno8ecxSB2ShHWQbM"   # <-- Nhập API key vào đây
DATA_FILE = "user_data.json"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

app = Flask(__name__)

# ================= USER STORAGE =================
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
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

def get_rank(q):
    ranks = [
        ("🪶 Tân học sinh", 5),
        ("📘 Chăm học", 25),
        ("🎓 Học sinh giỏi", 125),
        ("🏆 Học bá", 625),
        ("👑 Thiên tài", 3125)
    ]
    for name, need in ranks:
        if q < need:
            stars = int((q / need) * 5)
            return f"{name} {'⭐'*stars}{'☆'*(5-stars)} ({q}/{need})"
    return f"{ranks[-1][0]} ⭐⭐⭐⭐⭐ (MAX)"

# ================= ROUTES =================

@app.route("/")
def index():
    return render_template("index.html")

# ---- hỏi bình thường ----
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_id = data.get("user_id")
    question = data.get("question")

    if not user_id or not question:
        return jsonify({"error": "Thiếu tham số!"}), 400

    init_user(user_id)
    user_data[str(user_id)]["questions"] += 1
    save_data()

    prompt = (
        "Bạn là trợ lý học tập thông minh, trả lời tiếng Việt rõ ràng.\n"
        f"Câu hỏi: {question}"
    )

    try:
        response = model.generate_content(prompt)
        answer = response.text
    except Exception as e:
        answer = f"⚠ Lỗi AI: {e}"

    return jsonify({
        "answer": answer,
        "rank": get_rank(user_data[str(user_id)]["questions"])
    })


# ---- upload file & ảnh ----
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "Không có tệp nào được tải lên!"}), 400

    user_id = request.form.get("user_id")
    f = request.files["file"]
    file_bytes = f.read()

    if not user_id:
        return jsonify({"error": "Thiếu user_id!"}), 400

    init_user(user_id)
    user_data[str(user_id)]["questions"] += 1
    save_data()

    try:
        response = model.generate_content([
            {"mime_type": f.mimetype, "data": file_bytes},
            {"text": "Hãy phân tích nội dung tệp này và trả lời bằng tiếng Việt."}
        ])
        answer = response.text
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "answer": answer,
        "rank": get_rank(user_data[str(user_id)]["questions"])
    })


# ================= MAIN =================
if __name__ == "__main__":
    app.run(debug=True)
