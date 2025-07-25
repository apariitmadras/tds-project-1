import os
import json
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# Fallback URLs
FALLBACK_COURSE_URL   = "https://tds.s-anand.net/#/2025-01/"
FALLBACK_DISCOURSE_URL = "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"

# Load & normalize context.json into a flat list of {"text","url"}
with open("context.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

CONTEXT_ENTRIES = []
if isinstance(raw, dict):
    # wrap the full course text
    course_text = raw.get("course_text", "").strip()
    if course_text:
        CONTEXT_ENTRIES.append({
            "text": course_text,
            "url": FALLBACK_COURSE_URL
        })
    for item in raw.get("discourse", []):
        if "text" in item and "url" in item:
            CONTEXT_ENTRIES.append(item)
else:
    CONTEXT_ENTRIES = raw

# initialize OpenAI client (v1.x)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "App is live. Use POST /api/ with JSON {\"question\": \"…\"}"
    })


@app.route("/api/", methods=["GET", "POST"])
def api():
    if request.method == "GET":
        return jsonify({
            "message": "Send your question via POST JSON: {\"question\": \"…\"}"
        })

    # POST:
    try:
        data = request.get_json(force=True)
        question = data.get("question", "").strip()
        if not question:
            return jsonify({"error": "Missing 'question' in request"}), 400

        # build a truncated context blob
        texts = [e["text"] for e in CONTEXT_ENTRIES]
        full_context = "\n\n".join(texts)
        if len(full_context) > 12000:
            full_context = full_context[:12000]

        # ask GPT
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant answering questions based only on the provided context."
                },
                {
                    "role": "user",
                    "content": f"Context:\n{full_context}\n\nQuestion: {question}"
                }
            ],
            temperature=0.2
        )
        answer = resp.choices[0].message.content.strip()

        # pick up to 5 matching source links
        seen = set()
        words = set(question.lower().split())
        links = []
        for entry in CONTEXT_ENTRIES:
            txt = entry["text"].lower()
            if any(w in txt for w in words):
                url = entry["url"]
                if url not in seen:
                    snippet = entry["text"].replace("\n", " ")[:200]
                    links.append({"text": snippet, "url": url})
                    seen.add(url)
            if len(links) >= 5:
                break

        # fallback
        if not links:
            links = [
                {"text": "Course content", "url": FALLBACK_COURSE_URL},
                {"text": "Discourse",      "url": FALLBACK_DISCOURSE_URL}
            ]

        return jsonify({"answer": answer, "links": links})

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "answer": f"Could not get answer from OpenAI. (Error: {str(e)})",
            "links": []
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
