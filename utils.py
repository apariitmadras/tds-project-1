def answer_question(question, image_path=None):
    # For now, just dummy logic. We'll improve it later.
    if "gpt" in question.lower():
        return (
            "You must use `gpt-3.5-turbo-0125`, even if AI Proxy supports `gpt-4o-mini`.",
            [
                {
                    "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939/4",
                    "text": "Use the model mentioned in the question."
                },
                {
                    "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939/3",
                    "text": "Use a tokenizer to get number of tokens."
                }
            ]
        )
    return ("I'm not sure how to answer that yet.", [])
