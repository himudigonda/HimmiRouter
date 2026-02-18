from openai import OpenAI

# 1. Connect to YOUR Routing Engine (running locally)
# In production, this would be "https://api.himmirouter.com/v1"
client = OpenAI(
    base_url="http://localhost:4000/v1",
    # 2. Authenticate with YOUR system
    # This validates the user against your Postgres DB
    api_key="sk-or-v1-n0LWiUwxobCts0UpVQ-mmLxO6MfkeT_j",
)

print("--- 1. Checking Your Routing Engine's Catalog ---")
models = client.models.list()
for m in models.data:
    print(f"- {m.id}")

print("\n--- 2. Routing a Request ---")
# The Client just says "I want GPT-5"
# Your Gateway (at localhost:4000) decides:
# - Is this user allowed?
# - Do they have credits?
# - Which provider should I use? (OpenAI? Azure? Fallback?)
# - How much do I charge them?
completion = client.chat.completions.create(
    model="gemini-2.5-pro",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Explain why a centralized router is better than a client SDK.",
        },
    ],
    stream=True,
)

for chunk in completion:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print("\n")
