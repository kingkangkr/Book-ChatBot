from openai import OpenAI
import config
from prompt_template import prompt_template

OPENAI_API_KEY = config.OPENAI_API_KEY
openai_client = OpenAI(api_key=OPENAI_API_KEY)
model = "gpt-3.5-turbo"

def chatgpt_generate(query):
    messages = [{
        "role": "system",
        "content" : "You are a helpful assistant, capable of answering questions about novels, including summaries and themes."},
        {
            "role": "user",
            "content": query
        }]
    response = openai_client.chat.completions.create(model=model, messages=messages)
    answer = response.choices[0].message.content
    return answer

answer = chatgpt_generate(prompt_template)
print(answer)