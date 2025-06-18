from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import openai

app = Flask(__name__)
CORS(app)

# Load context
with open("context.json", "r", encoding="utf-8") as f:
    context_data = json.load(f)

course_text = context_data.get("course_text", "")
discourse_entries = context_data.get("discourse", [])

# Initialize OpenAI client (for SDK >= 1.0.0)
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def answer_question(question):
    # Prepare context with matching discourse entries
    context_parts = [course_text]
    links_used = []

    for post in discourse_entries:
        text = post.get("text", "")
        url = post.get("url", "")
        if any(q.lower() in text.lower() for q in question.split()):
            context_parts.append(f"{text}\n(Source: {url})")
            links_used.append({"url": url, "text": text[:80] + "..."})

    # Limit context size
    final_context = "\n\n".join(context_parts)[:10000]

    prompt = f"""
You are a helpful TA for the IIT Madras TDS course. Use the context below to answer the question.
Only include source URLs that helped you answer. If unsure, say you don't know.

Context:
{final_context}

Question: {question}
Answer:
""".strip()

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content.strip()
        return answer, links_used if links_used else [
            {"url": "https://tds.s-anand.net/#/2025-01/", "text": "Course content"},
            {"url": "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34", "text": "Discourse"}
        ]
    except Exception as e:
        return f"Could not get answer from OpenAI. (Error: {e})", []

@app.route("/")
def home():
    return "TDS Virtual TA API is live!"

@app.route("/api/", methods=["POST"])
def api():
    try:
        data = request.get_json()
        question = data.get("question", "").strip()

        if not question:
            return jsonify({"error": "Question is required."}), 400

        answer, links = answer_question(question)
        return jsonify({"answer": answer, "links": links})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
