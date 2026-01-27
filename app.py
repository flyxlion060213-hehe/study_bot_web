import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Cấu hình API Key từ Render Environment
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        user_query = data.get('question') # Nhận biến 'question' từ JS
        
        if not user_query:
            return jsonify({"answer": "Bạn chưa nhập gì cả!", "rank": "Hệ thống"})

        response = model.generate_content(user_query)
        
        # Trả về đúng khóa 'answer' để JS đọc được
        return jsonify({
            "answer": response.text,
            "rank": "Mộng Cam AI"
        })
    except Exception as e:
        print(f"Lỗi Server: {e}")
        return jsonify({
            "answer": "Mộng Cam đang bận hoặc API Key bị lỗi. Hãy kiểm tra lại cấu hình trên Render!",
            "rank": "Lỗi"
        })

if __name__ == '__main__':
    app.run()
