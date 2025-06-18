from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import json
import os

app = Flask(__name__)
CORS(app)

# Load combined context from JSON
with open("context.json") as f:
    context_data = json.load(f)

course_text = context_data.get("course_text", "")
discourse_entries = context_data.get("discourse", [])

# Set your OpenAI API key (from environment variable or directly here for testing)
openai.api_key = os.environ.get("OPENAI_API_KEY")  # safer for Render

def answer_question(question):
    # Prepare prompt: include course text + relevant discourse texts
    context_parts = [course_text]

    links_used = []

    for post in discourse_entries:
        text = post.get("text", "")
        url = post.get("url", "")
        if any(q.lower() in text.lower() for q in question.split()):  # simple keyword match
            context_parts.append(f"{text}\n(Source: {url})")
            links_used.append({"url": url, "text": text[:80] + "..."})

    # Limit content for token safety
    final_context = "\n\n".join(context_parts)[:10000]

    prompt = f"""You are a helpful TA for the IIT Madras TDS course. Use the following context to answer the question. Be concise and include source URLs if available.

Context:
{final_context}

Question: {question}
Answer:"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content.strip()
        return answer, links_used if links_used else [{"url": "https://tds.s-anand.net/#/2025-01/", "text": "Course content"}]
    except Exception as e:
        return f"Could not get answer from OpenAI. (Error: {e})", []

@app.route('/')
def home():
    return "TDS Virtual TA API is live."

@app.route('/api/', methods=['POST'])
def api():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Question is required."}), 400

    answer, links = answer_question(question)
    return jsonify({
        "answer": answer,
        "links": links
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000, debug=True)
