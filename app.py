import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        data = request.json
        question = data.get('question')

        if not api_key:
            return jsonify({"answer": "Thiếu API Key trên Render!", "rank": "Lỗi"})

        # URL gọi API Gemini bản v1 chính thức
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": question}]}]
        }

        response = requests.post(url, headers=headers, json=payload)
        res_data = response.json()

        # Kiểm tra kết quả
        if "candidates" in res_data:
            answer = res_data['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"answer": answer, "rank": "Mộng Cam AI"})
        else:
            # Hiện thông báo lỗi chi tiết từ Google nếu có
            error_msg = res_data.get("error", {}).get("message", str(res_data))
            return jsonify({"answer": f"Google báo lỗi: {error_msg}", "rank": "Lỗi"})

    except Exception as e:
        return jsonify({"answer": f"Lỗi hệ thống: {str(e)}", "rank": "Lỗi"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
