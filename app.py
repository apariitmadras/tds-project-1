from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import json
import re

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load context from JSON
with open("context.json", "r", encoding="utf-8") as f:
    context_data = json.load(f)

course_text = context_data.get("course_text", "")
discourse = context_data.get("discourse", "")

def extract_relevant_passages(question, full_text, max_chars=4000):
    keywords = [w.lower() for w in re.findall(r'\w+', question) if len(w) > 3]
    lines = full_text.splitlines()
    matched = [line for line in lines if any(kw in line.lower() for kw in keywords)]
    # join and trim
    return "\n".join(matched)[:max_chars] if matched else full_text[:max_chars]

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

        # Reduce context dynamically
        course_snippet = extract_relevant_passages(question, course_text)
        discourse_snippet = extract_relevant_passages(question, discourse)

        system_msg = (
            "You are a helpful assistant for the Tools in Data Science course at IIT Madras. "
            "Answer the student's question based on the context below. If there's not enough info, say so.\n\n"
            f"Course Content:\n{course_snippet}\n\nDiscourse:\n{discourse_snippet}"
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": question}
            ],
            temperature=0.2,
        )

        answer_text = response.choices[0].message.content.strip()

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
