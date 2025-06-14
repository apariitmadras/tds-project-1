from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/', methods=['POST'])
def api():
    data = request.get_json()
    question = data.get('question', '')
    return jsonify({"answer": "This is a placeholder answer."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
