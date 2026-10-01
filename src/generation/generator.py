from transformers import pipeline


generator = pipeline(
    "text-generation",
    model="google/flan-t5-small",
)


def generate_answer(prompt: str) -> str:
    """
    Generate an answer from a text prompt.
    """
    result = generator(
        prompt,
        max_new_tokens=100,
    )

    return result[0]["generated_text"]