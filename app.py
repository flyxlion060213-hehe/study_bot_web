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
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return jsonify({"answer": "Thiếu API Key trên Render!", "rank": "Hệ thống"})

        genai.configure(api_key=api_key)
        
        # SỬA Ở ĐÂY: Thêm 'models/' vào trước tên model
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        data = request.json
        question = data.get('question')

        # Thêm cấu hình an toàn (tùy chọn nhưng giúp bot trả lời mượt hơn)
        response = model.generate_content(question)
        
        if response.text:
            return jsonify({"answer": response.text, "rank": "Mộng Cam AI"})
        else:
            return jsonify({"answer": "AI trả về kết quả trống.", "rank": "Hệ thống"})

    except Exception as e:
        # Nếu vẫn lỗi, nó sẽ hiện lỗi chi tiết tại đây
        return jsonify({"answer": f"Lỗi 404 đã sửa nhưng gặp lỗi mới: {str(e)}", "rank": "Lỗi"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
