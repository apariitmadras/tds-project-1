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

        # Optional image processing (if needed later)
        if image_b64:
            image_bytes = base64.b64decode(image_b64)
            # process/save image here if needed

        from utils import answer_question
        answer, links = answer_question(question)

        return jsonify({
            'answer': answer,
            'links': links
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
