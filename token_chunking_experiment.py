from transformers import AutoTokenizer


tokenizer = AutoTokenizer.from_pretrained(
    "sentence-transformers/all-MiniLM-L6-v2"
)


text = """
one two three four five six seven eight
nine ten eleven twelve thirteen fourteen fifteen sixteen
seventeen eighteen nineteen twenty twentyone twentytwo
"""


tokens = tokenizer.encode(
    text,
    add_special_tokens=False
)


chunk_size = 8
overlap = 2

chunks = []

start = 0

while start < len(tokens):
    end = start + chunk_size

    chunk = tokens[start:end]

    chunks.append(chunk)

    start = end - overlap


for i, chunk in enumerate(chunks):
    decoded_chunk = tokenizer.decode(chunk)

    print(f"Chunk {i + 1}:")
    print(decoded_chunk)
    print("Token count:", len(chunk))
    print()