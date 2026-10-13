from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


MODEL_NAME = "google/flan-t5-small"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)


def generate_answer(prompt: str) -> str:
    """
    Generate an answer from a text prompt.
    """

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
    )

    outputs = model.generate(
        **inputs,
        max_new_tokens=100,
    )

    answer = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True,
    )

    return answer


def is_context_relevant(question: str, context: str) -> bool:
    """
    Check whether the context directly answers the question.
    Fail safely if the model gives an unexpected response.
    """

    prompt = f"""
    Determine whether the context contains information that directly
    answers the question.

    Reply with only yes or no.

    Question:
    {question}

    Context:
    {context}

    Does the context directly answer the question?
    """

    result = generate_answer(prompt).strip().lower()

    return result == "yes"
