from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import json

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load context from JSON file
with open("context.json", "r", encoding="utf-8") as f:
    CONTEXT = json.load(f)

@app.route("/")
def home():
    return "TDS Virtual TA API is live. Use /api/ endpoint to POST questions."

@app.route("/api/", methods=["POST"])
def answer():
    try:
        data = request.get_json()
        question = data.get("question", "").strip()

        if not question:
            return jsonify({"error": "Missing question field"}), 400

        # Build system message for grounding
        system_msg = (
            "You are a helpful assistant for the Tools in Data Science course at IIT Madras. "
            "Answer the student's question using the context below. If the context is insufficient, say so.\n\n"
            f"Context:\n{CONTEXT['course_text']}\n\n{CONTEXT['discourse']}"
        )

        # OpenAI chat completion (new SDK)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",  # or gpt-4o, if preferred
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": question}
            ],
            temperature=0.2,
        )

        answer_text = response.choices[0].message.content.strip()

        # Include useful links (static for now)
        links = [
            {"text": "Course content", "url": "https://tds.s-anand.net/#/2025-01/"},
            {"text": "Discourse", "url": "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"}
        ]

        return jsonify({
            "answer": answer_text,
            "links": links
        })

    except Exception as e:
        return jsonify({
            "answer": f"Could not get answer from OpenAI. (Error: {e})",
            "links": []
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
