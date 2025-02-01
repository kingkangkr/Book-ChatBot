import pandas as pd
import numpy as np
from scipy.spatial.distance import cosine
from ast import literal_eval
from dotenv import load_dotenv
import os
from openai import OpenAI
import re

# 데이터 로드
dt = pd.read_csv('data/filtered_booksummaries.csv')
dt['Parsed Embedding'] = dt['Summarized Plot Embedding'].apply(literal_eval)  # 안전한 변환

# 코사인 유사도 기반 추천 함수
def recommend_books_by_plot(book_title, top_n=3):
    selected_books = dt[dt['Book title'] == book_title]
    if selected_books.empty:
        print(f"Error: Book title '{book_title}' not found in the dataset.")
        return []

    selected_embedding = selected_books.iloc[0]['Parsed Embedding']
    
    # 데이터프레임 복사 후 변경 (원본 데이터 보호)
    dt_copy = dt.copy()
    dt_copy['Similarity'] = dt_copy['Parsed Embedding'].apply(lambda emb: 1 - cosine(selected_embedding, emb))
    
    # 가장 유사한 top_n 책 반환
    top_books = dt_copy[dt_copy['Book title'] != book_title].nlargest(top_n, 'Similarity')[['Book title', 'Similarity']]
    return top_books.values.tolist()

# OpenAI API 초기화
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)
model = "gpt-4o-mini"

def chatgpt_generate(prompts):
    messages = [{"role": "system", "content": "You are a helpful assistant."}] + prompts
    response = openai_client.chat.completions.create(model=model, messages=messages)
    return [choice.message.content for choice in response.choices]

# 스포일러 필터링 함수
def contains_spoiler(text):
    spoiler_patterns = [
        r"죽[음었이다]",  # "죽음", "죽었다", "죽이다" 등
        r"사망",         # "사망했다"
        r"범인",         # "범인은" 같은 문장 방지
        r"결말",         # "결말은 ~" 같은 문장 방지
        r"반전"          # "반전이 있다" 방지
    ]
    
    for pattern in spoiler_patterns:
        if re.search(pattern, text):
            return True
    return False

def recommend_and_explain(book_title, top_n=3):
    recommendations = recommend_books_by_plot(book_title, top_n=top_n)
    if not recommendations:
        return

    prompts = []
    for title, similarity in recommendations:
        book_data = dt[dt['Book title'] == title].iloc[0]
        summarized_plot = book_data['Summarized Plot Summary']

        prompt = (
            f"책 제목: {title}\n"
            f"추천 이유: '{book_title}'과 유사한 줄거리를 가지고 있습니다. "
            f"두 책이 어떤 점에서 비슷한지 간단히 설명해 주세요.\n\n"
            f" 주의: 결말, 주요 반전, 인물의 생사 여부, 범인 등의 스포일러를 포함하지 마세요. "
            f"독자가 직접 책을 읽을 수 있도록 흥미로운 요소만 설명하세요.\n\n"
            f"'{book_title}' 요약: {dt[dt['Book title'] == book_title].iloc[0]['Summarized Plot Summary']}\n"
            f"'{title}' 요약: {summarized_plot}\n\n"
        )
        prompts.append({"role": "user", "content": prompt})

    explanations = chatgpt_generate(prompts)

    print(f" '{book_title}'와(과) 비슷한 책 추천:")
    for (title, similarity), explanation in zip(recommendations, explanations):
        print(f"\n🔹 {title} (유사도: {similarity:.4f})")
        
        # 스포일러 필터링
        if contains_spoiler(explanation):
            print(" 스포일러 가능성이 있는 설명을 자동 제거했습니다.")
        else:
            print(f"추천 이유: {explanation}\n")

# 테스트 실행
query = "Brave New World"
recommend_and_explain(query)
