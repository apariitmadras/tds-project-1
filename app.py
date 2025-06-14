from flask import Flask, request, jsonify
import base64

app = Flask(__name__)

@app.route('/api/', methods=['GET', 'POST'])
def api():
    if request.method == 'GET':
        return jsonify({"message": "API is running. Use POST with JSON payload to interact."}), 200

    try:
        data = request.get_json()
        question = data.get('question', '')
        image_b64 = data.get('image')

        if not question:
            return jsonify({'error': 'Question is required'}), 400

        # Optional image handling
        if image_b64:
            try:
                image_bytes = base64.b64decode(image_b64)
                # You can process the image here if needed
            except Exception as e:
                return jsonify({'error': f'Invalid image encoding: {str(e)}'}), 400

        # Your main logic here
        from utils import answer_question  # Ensure utils.py has this function
        answer, links = answer_question(question)

        return jsonify({'answer': answer, 'links': links})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
