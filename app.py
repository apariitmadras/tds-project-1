from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import openai

app = Flask(__name__)
CORS(app)  # ✅ Enables CORS for all routes

# Load context.json
with open("context.json", "r") as f:
    context_data = json.load(f)
context_text = "\n\n".join([item["text"] for item in context_data])

# OpenAI client setup
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/')
def home():
    return "TDS Virtual TA API is live."

@app.route('/api/', methods=['POST', 'OPTIONS'])  # ✅ Accept OPTIONS preflight
def api():
    if request.method == 'OPTIONS':
        return '', 204  # ✅ Handle preflight requests

    try:
        data = request.get_json()
        question = data.get("question", "")
        image_b64 = data.get("image", None)  # Optional: if images are included

        if not question:
            return jsonify({"error": "No question provided"}), 400

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful TA for IITM's TDS course. Use only the context below."},
                {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion:\n{question}"}
            ]
        )
        answer = response.choices[0].message.content.strip()

        return jsonify({
            "answer": answer,
            "links": [
                {"text": "Course content", "url": "https://tds.s-anand.net/#/2025-01/"},
                {"text": "Discourse", "url": "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"}
            ]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
