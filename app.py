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
        question = request.json.get('question')

        # Dùng URL bản v1beta với model flash - Đây là bản có tỉ lệ chạy cao nhất
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        headers = {'Content-Type': 'application/json'}
        payload = {"contents": [{"parts": [{"text": question}]}]}
        
        response = requests.post(url, headers=headers, json=payload)
        res_data = response.json()
        
        if "candidates" in res_data:
            answer = res_data['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"answer": answer, "rank": "Mộng Cam AI"})
        
        # Nếu lỗi, trả về toàn bộ nội dung để soi lỗi
        return jsonify({"answer": f"Chi tiết lỗi từ Google: {res_data}", "rank": "Lỗi"})
            
    except Exception as e:
        return jsonify({"answer": f"Lỗi Python: {str(e)}", "rank": "Lỗi"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
