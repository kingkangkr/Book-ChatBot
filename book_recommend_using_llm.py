import pandas as pd
from scipy.spatial.distance import cosine
import numpy as np

dt = pd.read_csv('data/booksummaries_embeddings_0_12839.csv')
# 코사인 유사도를 계산하여 가장 비슷한 책 3권 추천 함수 (줄거리 임베딩 기반)
def recommend_books_by_plot(book_title, top_n=3):
    # 선택한 책의 데이터 가져오기
    selected_books = dt[dt['Book title'] == book_title]
    
    if selected_books.empty:  # 책 제목이 없는 경우 처리
        print(f"Error: Book title '{book_title}' not found in the dataset.")
        return []

    selected_book = selected_books.iloc[0]

    # 선택한 책의 줄거리 임베딩 추출
    selected_embedding = eval(selected_book['Summarized Plot Embedding'])

    # 코사인 유사도를 저장할 리스트
    similarities = []

    for _, row in dt.iterrows():
        if row['Book title'] != book_title:  # 자기 자신은 제외
            other_embedding = eval(row['Summarized Plot Embedding'])
            similarity = 1 - cosine(selected_embedding, other_embedding)  # 코사인 유사도 계산
            similarities.append((row['Book title'], similarity))

    # 유사도를 기준으로 정렬하여 상위 n개 선택
    top_books = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_n]

    # 추천 결과 반환
    return top_books
from dotenv import load_dotenv
import os
from openai import OpenAI
# OpenAI API 초기화
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

model = "gpt-4o-mini"  # 사용할 OpenAI 모델

# ChatGPT 요청 함수
def chatgpt_generate(query):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": query}
    ]
    response = openai_client.chat.completions.create(model=model, messages=messages)
    answer = response.choices[0].message.content
    return answer

# 책 추천 + 설명 함수
def recommend_and_explain(book_title, top_n=3):
    # 추천된 책 리스트 가져오기
    recommendations = recommend_books_by_plot(book_title, top_n=top_n)

    # 추천 결과에 대해 설명 생성
    explanations = []
    for title, similarity in recommendations:
        # 추천된 책의 줄거리 가져오기
        book_data = dt[dt['Book title'] == title].iloc[0]
        summarized_plot = book_data['Summarized Plot Summary']

        # LLM에게 설명 요청
        prompt = (
            f"책 제목: {title}\n"
            f"추천 이유: 이 책은 '{book_title}'과 유사한 줄거리를 가지고 있습니다. "
            f"두 책이 어떤 점에서 비슷한지 간단히 설명해 주세요.\n\n"
            f"'{book_title}' 요약: {dt[dt['Book title'] == book_title].iloc[0]['Summarized Plot Summary']}\n"
            f"'{title}' 요약: {summarized_plot}\n\n"
        )
        try:
            explanation = chatgpt_generate(prompt)
        except Exception as e:
            explanation = f"추천 이유 생성 중 오류 발생: {e}"

        # 설명 결과 저장
        explanations.append((title, similarity, explanation))

    # 최종 결과 출력
    print(f"Books similar to '{book_title}':")
    for title, similarity, explanation in explanations:
        print(f"\n{title} (Similarity: {similarity:.4f})")
        print(f"추천 이유: {explanation}\n")

# 테스트 실행
query = "Brave New World"
recommend_and_explain(query)
