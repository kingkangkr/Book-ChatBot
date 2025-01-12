import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)
print(OPENAI_API_KEY)
model = "gpt-4o-mini"

def chatgpt_generate(query):
    messages = [{
        "role": "system",
        "content" : "You are a helpful assistant."},
        {
            "role": "user",
            "content": query
        }]
    response = openai_client.chat.completions.create(model=model, messages=messages)
    answer = response.choices[0].message.content
    return answer
query = "Hello, can you confirm the API is working?"
try:
    answer = chatgpt_generate(query)
    print("Response from OpenAI API:", answer)
except Exception as e:
    print("Error:", e)
