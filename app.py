from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import openai
import json

app = Flask(__name__)
CORS(app)

# Load context JSON once at startup
with open("context.json", "r") as f:
    context_data = json.load(f)
context_text = "\n\n".join([item["text"] for item in context_data])

# Initialize OpenAI client (ensure OPENAI_API_KEY is set in env)
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def home():
    return "TDS Virtual TA API is live."

@app.route("/api/", methods=["GET", "POST", "OPTIONS"])
def api():
    # Handle CORS preflight
    if request.method == "OPTIONS":
        return "", 204

    # Always return this shape on GET
    if request.method == "GET":
        return jsonify({
            "answer": "TDS Virtual TA is running. Send a POST with {'question': '...'} to get answers.",
            "links": [
                {"text": "Course content", "url": "https://tds.s-anand.net/#/2025-01/"},
                {"text": "Discourse",     "url": "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"}
            ]
        })

    # POST handling
    data = request.get_json() or {}
    question = data.get("question", "").strip()

    # If no question provided, still return 200 with valid shape
    if not question:
        return jsonify({
            "answer": "Please provide a question in the request body.",
            "links": [
                {"text": "Course content", "url": "https://tds.s-anand.net/#/2025-01/"},
                {"text": "Discourse",     "url": "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"}
            ]
        })

    # Attempt real OpenAI call, fallback to placeholder on any error
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful TA for IITM's Tools in Data Science course. Answer using only the provided context."},
                {"role": "user",   "content": f"Context:\n{context_text}\n\nQuestion: {question}"}
            ]
        )
        answer = response.choices[0].message.content.strip()
    except Exception:
        answer = f"You asked: {question}"

    return jsonify({
        "answer": answer,
        "links": [
            {"text": "Course content", "url": "https://tds.s-anand.net/#/2025-01/"},
            {"text": "Discourse",     "url": "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"}
        ]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
