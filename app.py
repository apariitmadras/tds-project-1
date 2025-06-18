from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import json
import os
import re

# Load OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

# Load context.json once at startup
with open("context.json", "r", encoding="utf-8") as f:
    context_data = json.load(f)

course_text = context_data.get("course_text", "")
discourse_entries = context_data.get("discourse", [])

@app.route("/")
def home():
    return "TDS Virtual TA API is live. Use POST /api/ to ask questions."

@app.route("/api/", methods=["POST"])
def answer():
    try:
        data = request.get_json()
        question = data.get("question", "")

        if not question:
            return jsonify({"answer": "No question provided", "links": []}), 400

        # Tokenize the question
        question_words = re.findall(r"\w+", question.lower())

        # Match relevant discourse posts
        context_parts = [course_text[:3000]]  # Include first part of course content
        used_urls = set()

        for post in discourse_entries:
            text = post.get("text", "")
            url = post.get("url", "")
            score = sum(word in text.lower() for word in question_words)
            if score >= 2:  # Use this post if 2+ keywords match
                context_parts.append(f"{text}\n(Source: {url})")
                used_urls.add((url, text[:100] + "..."))

        final_context = "\n\n".join(context_parts)

        # Build the prompt
        system_msg = (
            "You are a helpful teaching assistant for the Tools in Data Science course. "
            "Answer the student's question using the context below. If the answer comes from a particular page, be specific and include it.\n\n"
            f"Context:\n{final_context}"
        )

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": question}
        ]

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",
            messages=messages,
            temperature=0.2,
        )

        answer_text = response["choices"][0]["message"]["content"]

        # Build the links list for final response
        links_used = [{"url": url, "text": text} for url, text in used_urls]

        return jsonify({
            "answer": answer_text,
            "links": links_used
        })

    except Exception as e:
        return jsonify({
            "answer": f"Could not get answer from OpenAI. (Error: {e})",
            "links": []
        }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
