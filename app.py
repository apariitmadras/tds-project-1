import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import traceback

app = Flask(__name__)
CORS(app)

# Load context
with open("context.json", "r", encoding="utf-8") as f:
    CONTEXT_ENTRIES = json.load(f)

FALLBACK_COURSE_URL = "https://tds.s-anand.net/#/2025-01/"
FALLBACK_DISCOURSE_URL = "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"

# Set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def home():
    return "App is live. Use /api/ to send POST requests."

@app.route("/api/", methods=["POST"])
def api():
    try:
        data = request.get_json()
        question = data.get("question")

        if not question:
            return jsonify({"error": "Missing 'question' in request"}), 400

        # Prepare context text for LLM
        all_chunks = [entry["text"] for entry in CONTEXT_ENTRIES]
        full_context = "\n\n".join(all_chunks)
        if len(full_context) > 12000:
            full_context = full_context[:12000]

        # Ask OpenAI
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant answering questions based only on the course and Discourse content provided."
                },
                {
                    "role": "user",
                    "content": f"Context:\n{full_context}\n\nQuestion: {question}"
                }
            ],
            temperature=0.2,
        )

        answer = completion.choices[0].message.content.strip()

        # Extract relevant links from context
        matched_links = []
        seen_urls = set()
        question_words = set(question.lower().split())

        for entry in CONTEXT_ENTRIES:
            if any(word in entry["text"].lower() for word in question_words):
                if entry["url"] not in seen_urls:
                    snippet = " ".join(entry["text"].split())[:200]
                    matched_links.append({"text": snippet, "url": entry["url"]})
                    seen_urls.add(entry["url"])
            if len(matched_links) >= 5:
                break

        if not matched_links:
            matched_links = [
                {"text": "Course content", "url": FALLBACK_COURSE_URL},
                {"text": "Discourse", "url": FALLBACK_DISCOURSE_URL}
            ]

        return jsonify({"answer": answer, "links": matched_links})

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "answer": f"Could not get answer from OpenAI. (Error: {str(e)})",
            "links": []
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
