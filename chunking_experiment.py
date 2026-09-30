text = """
Employees must change their password every 90 days.
Passwords must contain at least 12 characters.
Two-factor authentication is required for administrative accounts.
Employees should report suspicious emails to the security team.
"""

words = text.split()

chunk_size = 10
overlap = 2

chunks = []

start = 0

while start < len(words):
    end = start + chunk_size
    chunk = words[start:end]

    chunks.append(chunk)

    start = end - overlap

for i, chunk in enumerate(chunks):
    print(f"Chunk {i + 1}:")
    print(" ".join(chunk))
    print()