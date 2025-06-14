from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/', methods=['POST'])
def api():
    data = request.get_json() or {}
    question = data.get('question', '')

    # Always return both answer and links
    return jsonify({
        "answer": f"You asked: {question}",
        "links": []      # empty list if you have no links to share
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
