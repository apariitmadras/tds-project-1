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

# Initialize OpenAI client using your environment variable
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def home():
    return "TDS Virtual TA API is live."

@app.route("/api/", methods=["GET", "POST", "OPTIONS"])
def api():
    # Handle CORS preflight
    if request.method == "OPTIONS":
        return "", 204

    # GET request – used for form checks
    if request.method == "GET":
        return jsonify({
            "answer": "TDS Virtual TA is running. Send a POST with {'question': '...'} to get answers.",
            "links": [
                {"text": "Course content", "url": "https://tds.s-anand.net/#/2025-01/"},
                {"text": "Discourse", "url": "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"}
            ]
        })

    # POST request – real Q&A
    data = request.get_json() or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "answer": "Please provide a question in the request body.",
            "links": [
                {"text": "Course content", "url": "https://tds.s-anand.net/#/2025-01/"},
                {"text": "Discourse", "url": "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"}
            ]
        })

    try:
        # OpenAI chat call with course context
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful TA for IITM's Tools in Data Science course. Use only the provided context to answer."
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context_text}\n\nQuestion: {question}"
                }
            ]
        )
        answer = response.choices[0].message.content.strip()

    except Exception as e:
        # Fallback if OpenAI fails
        answer = f"Could not get answer from OpenAI. (Error: {str(e)})"

    return jsonify({
        "answer": answer,
        "links": [
            {"text": "Course content", "url": "https://tds.s-anand.net/#/2025-01/"},
            {"text": "Discourse", "url": "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"}
        ]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
