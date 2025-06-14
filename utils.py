def load_content():
    with open('tds_clean.txt', 'r', encoding='utf-8') as f:
        return f.read()

course_text = load_content()

def answer_question(question):
    # Naive search — find 3 most relevant lines
    lines = course_text.split('\n')
    results = [line for line in lines if question.lower() in line.lower()]

    top_results = results[:3] if results else ["Sorry, I couldn't find an exact answer. Try rephrasing your question."]
    
    # Dummy example links (you can improve later)
    links = [{"url": "https://tds.s-anand.net/#/", "text": "Course page"}]

    return '\n'.join(top_results), links
