from flask import Flask, request, render_template, jsonify
import google.generativeai as genai
import os, json

# ======================
# CẤU HÌNH
# ======================
GEMINI_API_KEY = "DAN_API_KEY_GEMINI_VAO_DAY"
DATA_FILE = "user_data.json"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)

# ======================
# KIẾN THỨC NỀN (SYSTEM KNOWLEDGE)
# ======================

PROVINCE_KNOWLEDGE = """
Bạn nắm vững kiến thức về tổ chức hành chính Việt Nam theo phương án 34 tỉnh, thành phố,
được tổng hợp theo định hướng của Thư viện Pháp Luật Việt Nam.

Nguyên tắc:
- Dùng tên hành chính chính thức.
- Không suy đoán nếu ngoài phạm vi pháp luật hiện hành.
- Trả lời phù hợp cho học sinh.

Danh sách 34 tỉnh, thành:
Hà Nội; TP. Hồ Chí Minh; Hải Phòng; Đà Nẵng; Cần Thơ; Thừa Thiên Huế; Quảng Ninh;
Thanh Hóa; Nghệ An; Hà Tĩnh; Quảng Bình; Quảng Trị; Quảng Nam; Quảng Ngãi;
Bình Định; Phú Yên; Khánh Hòa; Lâm Đồng; Đắk Lắk; Gia Lai; Kon Tum;
Bình Thuận; Đồng Nai; Bình Dương; Bà Rịa – Vũng Tàu; Tây Ninh; Long An;
Tiền Giang; Bến Tre; Trà Vinh; Vĩnh Long; An Giang; Kiên Giang; Cà Mau.
"""

CHEMISTRY_RULES = """
Quy tắc hoá học:
- Khi hỏi về tên chất hoá học, luôn ưu tiên TÊN QUỐC TẾ (tiếng Anh – IUPAC).
- KHÔNG dùng phiên âm tiếng Việt kiểu cũ.

Ví dụ:
- H2SO4 → Sulfuric acid
- HNO3 → Nitric acid
- NaCl → Sodium chloride
- CO2 → Carbon dioxide
- NH3 → Ammonia
- CaCO3 → Calcium carbonate

Nếu cần, có thể ghi chú thêm trong ngoặc (tên cũ) để học sinh dễ hiểu.
"""

SYSTEM_PROMPT = f"""
Bạn là trợ lý học tập AI thông minh cho học sinh Việt Nam.
Luôn trả lời bằng tiếng Việt rõ ràng, dễ hiểu, chính xác.

{PROVINCE_KNOWLEDGE}

{CHEMISTRY_RULES}
"""

# ======================
# LOAD / SAVE USER DATA
# ======================
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
            return f"{name} {'⭐'*stars}{'☆'*(5-stars)} ({questions}/{need})"
    return "👑 Thiên tài ⭐⭐⭐⭐⭐ (MAX)"

# ======================
# ROUTES
# ======================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_id = data.get("user_id")
    question = data.get("question")

    if not user_id or not question:
        return jsonify({"error": "Thiếu dữ liệu"}), 400

    init_user(user_id)
    user_data[str(user_id)]["questions"] += 1
    save_data()

    prompt = f"""
{SYSTEM_PROMPT}

Câu hỏi của học sinh:
{question}
"""

    try:
        response = model.generate_content(prompt)
        answer = response.text
    except Exception as e:
        answer = f"⚠️ Lỗi Gemini API: {e}"

    return jsonify({
        "answer": answer,
        "rank": get_rank(user_data[str(user_id)]["questions"])
    })

# ======================
# RUN
# ======================
if __name__ == "__main__":
    app.run(debug=True)
