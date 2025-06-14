import re

def load_content():
    with open('tds_clean.txt', 'r', encoding='utf-8') as f:
        return f.read().splitlines()


COURSE_LINES = load_content()

def answer_question(question):
    q = question.lower().strip()
    keywords = [w for w in re.findall(r'\w+', q) if len(w) > 3]

   
    matches = []
    for line in COURSE_LINES:
        low = line.lower()
        if any(kw in low for kw in keywords):
            matches.append(line.strip())
        if len(matches) >= 3:
            break

    if not matches:
        answer = "Sorry, I couldn't find an exact answer. Try rephrasing your question."
    else:
        answer = "Here are some relevant excerpts:\n" + "\n".join(matches)

    links = [
        {"text": "Course page", "url": "https://tds.s-anand.net/#/2025-01/"}
    ]
    return answer, links
