from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import openai
import json

app = Flask(__name__)
CORS(app)

# Load context.json once
with open("context.json", "r") as f:
    context_data = json.load(f)
context_text = "\n\n".join([item["text"] for item in context_data])

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/')
def home():
    return "TDS Virtual TA API is live."

@app.route('/api/', methods=['GET', 'POST', 'OPTIONS'])
def api():
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 204

    # If it's a GET, return a dummy but valid shape
    if request.method == 'GET':
        return jsonify({
            "answer": "TDS Virtual TA is running. Send a POST with {'question': '...'} to get answers.",
            "links": [
                {"text": "Course content", "url": "https://tds.s-anand.net/#/2025-01/"},
                {"text": "Discourse", "url": "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"}
            ]
        })

    # Otherwise it's a POST with a real question
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "Question is required", "links": []}), 400

    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a TA for the TDS course. Answer using the context."},
                {"role": "user", "content": f"Context:\n{context_text}\n\nQ: {question}"}
            ]
        )
        answer = resp.choices[0].message.content.strip()
        return jsonify({
            "answer": answer,
            "links": [
                {"text": "Course content", "url": "https://tds.s-anand.net/#/2025-01/"},
                {"text": "Discourse", "url": "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"}
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e), "links": []}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
