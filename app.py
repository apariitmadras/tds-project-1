from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import answer_question    # bring in your Q&A logic

app = Flask(__name__)
CORS(app)

@app.route('/api/', methods=['POST'])
def api():
    data = request.get_json() or {}
    question = data.get('question', '')

    if not question:
        return jsonify({"error": "Question is required", "links": []}), 400

    # this returns (answer_text, links_list)
    answer, links = answer_question(question)

    return jsonify({
        "answer": answer,
        "links": links
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
