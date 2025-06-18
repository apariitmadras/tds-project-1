import os
import json
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# Load context entries: a list of {"text": "...", "url": "..."}
with open("context.json", "r", encoding="utf-8") as f:
    CONTEXT_ENTRIES = json.load(f)

openai.api_key = os.getenv("OPENAI_API_KEY")

FALLBACK_COURSE_URL = "https://tds.s-anand.net/#/2025-01/"
FALLBACK_DISCOURSE_URL = "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"

# Global error handler to always return JSON
@app.errorhandler(Exception)
def handle_unexpected_error(error):
    response = jsonify({
        "answer": f"Internal server error: {str(error)}",
        "links": []
    })
    response.status_code = 500
    return response

@app.route("/")
def home():
    return "App is live. POST your JSON to /api/"

@app.route("/api/", methods=["POST"])
def api():
    data = request.get_json(force=True)
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "Missing 'question' in request"}), 400

    # Build the full context string
    all_texts = [entry["text"] for entry in CONTEXT_ENTRIES]
    full_context = "\n\n".join(all_texts)
    if len(full_context) > 12000:
        full_context = full_context[:12000] + "\n\n...[truncated]"

    # Call OpenAI
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant. Answer ONLY using the provided context."
                    )
                },
                {
                    "role": "user",
                    "content": f"Context:\n{full_context}\n\nQuestion: {question}"
                }
            ],
            temperature=0.2,
        )
        answer = resp.choices[0].message.content.strip()
    except Exception as e:
        return jsonify({
            "answer": f"Could not get answer from OpenAI. (Error: {str(e)})",
            "links": []
        }), 200

    # Pick out which context entries contributed
    # by checking word overlap between answer & entry text.
    def long_words(s):
        return {w.lower() for w in re.findall(r"\w+", s) if len(w) > 4}

    ans_words = long_words(answer)
    matched = []
    for entry in CONTEXT_ENTRIES:
        entry_words = long_words(entry["text"])
        if len(ans_words & entry_words) >= 2:
            matched.append({"url": entry["url"], "text": entry["text"][:200]})
        if len(matched) >= 5:
            break

    if not matched:
        matched = [
            {"url": FALLBACK_COURSE_URL,    "text": "Course content"},
            {"url": FALLBACK_DISCOURSE_URL, "text": "Discourse forum"}
        ]

    return jsonify({"answer": answer, "links": matched}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
