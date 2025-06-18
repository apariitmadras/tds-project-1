from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import json
import os

app = Flask(__name__)
CORS(app)

# Load your OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load the context.json file
with open("context.json", "r", encoding="utf-8") as f:
    context_data = json.load(f)

course_text = context_data.get("course_text", "")

# Process discourse content safely
discourse_list = context_data.get("discourse", [])
if isinstance(discourse_list, list) and isinstance(discourse_list[0], dict):
    discourse_text = "\n".join([item.get("text", "") for item in discourse_list])
else:
    discourse_text = "\n".join(discourse_list) if isinstance(discourse_list, list) else discourse_list

discourse_links = [
    {"url": item.get("url", ""), "text": item.get("text", "")}
    for item in discourse_list if isinstance(item, dict)
]

@app.route("/")
def home():
    return "App is live. Use /api/ to POST questions."

@app.route("/api/", methods=["POST"])
def answer_question():
    try:
        data = request.get_json()
        question = data.get("question", "").strip()

        if not question:
            return jsonify({"answer": "No question provided.", "links": []}), 400

        # Combine prompt context
        prompt = f"""
You are a helpful assistant for the IITM Online BS degree program.
Answer the student's question based ONLY on the following Tools in Data Science course content and forum discussions.
Provide relevant links if available, otherwise say "no link available".

Course content:
{course_text[:8000]}

Forum discussions:
{discourse_text[:8000]}

Question: {question}
Answer:"""

        # Send to OpenAI (gpt-3.5 or gpt-4o)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",  # or "gpt-4o"
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        reply = response["choices"][0]["message"]["content"]

        # Find matching links from discourse if keywords are mentioned
        matched_links = []
        for item in discourse_links:
            if any(word.lower() in reply.lower() for word in item["text"].split()):
                matched_links.append(item)
            if len(matched_links) >= 5:
                break

        return jsonify({
            "answer": reply.strip(),
            "links": matched_links
        })

    except Exception as e:
        return jsonify({
            "answer": f"Could not get answer from OpenAI. (Error: {str(e)})",
            "links": []
        }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
