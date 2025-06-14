from flask import Flask, request, jsonify
from flask_cors import CORS  # NEW

app = Flask(__name__)
CORS(app)  # NEW

@app.route('/')
def home():
    return "App is live. Use /api/ to send requests."

@app.route('/api/', methods=['GET', 'POST'])
def api():
    if request.method == 'GET':
        return jsonify({"message": "API is running. Use POST with JSON payload to interact."})
    elif request.method == 'POST':
        data = request.get_json()
        return jsonify({"you_sent": data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
