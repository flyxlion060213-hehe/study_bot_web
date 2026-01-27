import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        # Lấy Key từ Environment của Render
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            return jsonify({"answer": "LỖI: Bạn chưa thêm biến GEMINI_API_KEY trên Render!", "rank": "Hệ thống"})

        # Cấu hình ngay trong hàm để đảm bảo Key luôn mới
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        data = request.json
        question = data.get('question')

        response = model.generate_content(question)
        
        if response.text:
            return jsonify({"answer": response.text, "rank": "Mộng Cam AI"})
        else:
            return jsonify({"answer": "AI trả về kết quả trống.", "rank": "Hệ thống"})

    except Exception as e:
        # Trả về lỗi thật để bạn nhìn thấy trên web
        return jsonify({"answer": f"Lỗi Gemini: {str(e)}", "rank": "Lỗi"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
