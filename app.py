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
        
        # Thử dùng URL trực tiếp nhất
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": question}]}]
        }
        
        response = requests.post(url, json=payload)
        res_data = response.json()
        
        if "candidates" in res_data:
            answer = res_data['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"answer": answer, "rank": "Mộng Cam AI"})
        else:
            # Nếu vẫn lỗi 404, trả về toàn bộ lỗi để kiểm tra
            return jsonify({"answer": f"Google vẫn báo lỗi: {res_data.get('error', {}).get('message', 'Unknown')}", "rank": "Lỗi"})
    except Exception as e:
        return jsonify({"answer": f"Lỗi: {str(e)}", "rank": "Lỗi"})

# Copy các route chemistry tương tự vào đây...

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
