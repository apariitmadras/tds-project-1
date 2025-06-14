from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import openai
import json

app = Flask(__name__)
CORS(app)  # Enables CORS

# Load context
with open("context.json", "r") as f:
    context = json.load(f)
context_text = "\n\n".join([item["text"] for item in context])

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def home():
    return "TDS Virtual TA API is live."

@app.route("/api/", methods=["POST", "OPTIONS"])
def ask():
    if request.method == "OPTIONS":
        return '', 204  # Handle CORS preflight

    try:
        data = request.get_json()
        question = data.get("question", "")

        if not question:
            return jsonify({"error": "No question provided"}), 400

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful teaching assistant for the IITM Tools in Data Science course. Use only the context provided.",
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context_text}\n\nQuestion: {question}",
                },
            ],
        )

        answer = response.choices[0].message.content.strip()

        return jsonify({
            "answer": answer,
            "links": [
                {"text": "Course content", "url": "https://tds.s-anand.net/#/2025-01/"},
                {"text": "Discourse", "url": "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"},
            ]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
