from flask import Flask, request, jsonify
from utils import answer_question
import base64

app = Flask(__name__)

@app.route('/api/', methods=['POST'])
def handle_query():
    data = request.get_json()
    question = data.get("question")
    image_data = data.get("image")

    # Save image if provided
    image_path = None
    if image_data:
        image_path = "temp_image.webp"
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image_data))

    # Get the answer
    answer, links = answer_question(question, image_path)

    return jsonify({
        "answer": answer,
        "links": links
    })

if __name__ == "__main__":
    app.run(debug=True)
