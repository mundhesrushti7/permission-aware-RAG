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