from flask import Flask, request, jsonify
from utils import answer_question
import base64

app = Flask(__name__)

@app.route('/')
def home():
    return 'TDS Virtual TA is running!'

@app.route('/api/', methods=['GET', 'POST'])
def api():
    try:
        data = request.get_json()
        question = data.get('question', '')
        image_b64 = data.get('image')

        if not question:
            return jsonify({'error': 'Question is required'}), 400

        # Optional: process image if needed later
        if image_b64:
            image_bytes = base64.b64decode(image_b64)
            # (You can save or process image if needed)

        answer, links = answer_question(question)

        return jsonify({
            'answer': answer,
            'links': links
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
