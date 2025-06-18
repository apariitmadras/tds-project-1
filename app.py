import os
import json
import re
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load context from context.json (should be a list of {"text": ..., "url": ...})
with open("context.json", "r", encoding="utf-8") as f:
    CONTEXT_ENTRIES = json.load(f)

openai.api_key = os.getenv("OPENAI_API_KEY")

FALLBACK_COURSE_URL = "https://tds.s-anand.net/#/2025-01/"
FALLBACK_DISCOURSE_URL = "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"

@app.route("/")
def home():
    return "App is live. Use /api/ to send questions."

@app.route("/api/", methods=["POST"])
def api():
    data = request.get_json()
    question = data.get("question")
    if not question:
        return jsonify({"error": "Missing 'question' in request"}), 400

    # Prepare full context as one string (truncate if too long)
    all_texts = [entry["text"] for entry in CONTEXT_ENTRIES]
    full_context = "\n\n".join(all_texts)
    if len(full_context) > 12000:
        full_context = full_context[:12000]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant answering questions based only on the course and Discourse content."
                },
                {
                    "role": "user",
                    "content": f"Context:\n{full_context}\n\nQuestion: {question}"
                }
            ],
            temperature=0.2
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        return jsonify({
            "answer": f"Could not get answer from OpenAI. (Error: {str(e)})",
            "links": []
        })

    # Extract answer-words (length ≥ 4) and match against context entries
    answer_words = set(re.findall(r"\w{4,}", answer.lower()))
    links = []
    for entry in CONTEXT_ENTRIES:
        txt = entry["text"].lower()
        common = sum(1 for w in answer_words if w in txt)
        if common >= 2:
            links.append({
                "text": entry["text"].replace("\n", " ")[:200],
                "url": entry["url"]
            })

    # If no links matched, fall back to generic
    if not links:
        links = [
            {"text": "Course content", "url": FALLBACK_COURSE_URL},
            {"text": "Discourse",     "url": FALLBACK_DISCOURSE_URL}
        ]

    return jsonify({"answer": answer, "links": links})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
