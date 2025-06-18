import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

# Setup
app = Flask(__name__)
CORS(app)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load context from context.json
with open("context.json", "r", encoding="utf-8") as f:
    context_data = json.load(f)

# Prepare context text
course_text = context_data.get("course_text", "")
discourse_data = context_data.get("discourse", [])

# Join discourse text if it's a list of dicts
if isinstance(discourse_data, list):
    discourse_text = "\n\n".join(item.get("text", "") for item in discourse_data)
else:
    discourse_text = discourse_data

# Combine both sources
combined_context = course_text + "\n\n" + discourse_text

# Link mapping for response
source_links = [
    {"text": "Course content", "url": "https://tds.s-anand.net/#/2025-01/"},
    {"text": "Discourse", "url": "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"},
]

@app.route("/")
def home():
    return "TDS Virtual TA API is live. Use the `/api/` endpoint."

@app.route("/api/", methods=["POST"])
def api():
    try:
        data = request.get_json()
        question = data.get("question", "")

        if not question.strip():
            return jsonify({"answer": "Please provide a valid question.", "links": []}), 400

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful teaching assistant for the Tools in Data Science (TDS) course at IIT Madras. "
                    "Answer questions using the provided context from the course page and Discourse forum. "
                    "Give specific, helpful, and concise answers."
                )
            },
            {
                "role": "user",
                "content": f"{combined_context}\n\nQuestion: {question}"
            }
        ]

        # Make OpenAI API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.5,
        )

        answer_text = response.choices[0].message.content.strip()

        return jsonify({
            "answer": answer_text,
            "links": source_links
        })

    except Exception as e:
        return jsonify({
            "answer": f"Could not get answer from OpenAI. (Error: {str(e)})",
            "links": []
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
