import openai
from openai import OpenAI

client = OpenAI(api_key="sk-xxxxxxxxxxxxxxxx")


try:
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Hello, OpenAI!"}
    ])
except openai.AuthenticationError:
    print("❌ API key is invalid or billing not set up.")
except Exception as e:
    print(f"⚠️ Error: {e}")