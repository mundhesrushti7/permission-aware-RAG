from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    "sentence-transformers/all-MiniLM-L6-v2"
)

text = "Employees must change their password every 90 days."

tokens = tokenizer.tokenize(text)
token_ids = tokenizer.encode(text, add_special_tokens=False)

print("Original text:")
print(text)

print("\nTokens:")
print(tokens)

print("\nNumber of tokens:")
print(len(tokens))

print("\nToken IDs:")
print(token_ids)