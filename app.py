import os
from flask import Flask, request, jsonify, render_template
import requests # Nhớ cài: pip install requests

app = Flask(__name__)

# Đọc API Key từ biến môi trường của Render
# Nếu chạy ở máy cá nhân mà chưa có biến này, nó sẽ báo lỗi để bạn biết
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    user_question = data.get('question')

    # Gọi Google Gemini API bằng Key bí mật từ server
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": user_question}]}]
    }
    
    response = requests.post(url, json=payload)
    result = response.json()

    try:
        answer = result['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"answer": answer, "rank": "AI Support"})
    except:
        return jsonify({"answer": "Lỗi API hoặc chưa cấu hình Key trên Render!", "rank": "Error"})

if __name__ == '__main__':
    app.run(debug=True)
