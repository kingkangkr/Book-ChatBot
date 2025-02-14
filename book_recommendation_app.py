import streamlit as st
import pandas as pd
import numpy as np
from scipy.spatial.distance import cosine
from dotenv import load_dotenv
import os
from openai import OpenAI
import ast
import concurrent.futures
import faiss

# Load API key for OpenAI
load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Load dataset
@st.cache_data
def load_data():
    dt = pd.read_csv('data/filtered_booksummaries.csv') #임베딩 데이터
    dt['Summarized Plot Embedding'] = dt['Summarized Plot Embedding'].apply(ast.literal_eval)
    return dt

dt = load_data()

# Optimized recommendation function
def recommend_books_by_plot_optimized(book_title, top_n=3):
    selected_books = dt[dt['Book title'].str.lower() == book_title.lower()]
    if selected_books.empty:
        return []
    selected_embedding = np.array(selected_books.iloc[0]['Summarized Plot Embedding'])
    all_embeddings = np.vstack(dt['Summarized Plot Embedding'].tolist())
    similarities = 1 - np.dot(all_embeddings, selected_embedding) / (
        np.linalg.norm(all_embeddings, axis=1) * np.linalg.norm(selected_embedding)
    )
    dt['similarity'] = similarities
    return dt[dt['Book title'].str.lower() != book_title.lower()].nlargest(top_n, 'similarity')[['Book title', 'similarity']].values

# ChatGPT explanation
def chatgpt_generate(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating explanation: {e}"

def generate_explanations(recommendations, book_title):
    explanations = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for title, _ in recommendations:
            # 추천된 책의 줄거리 가져오기
            book_data = dt[dt['Book title'] == title].iloc[0]
            summarized_plot = book_data['Summarized Plot Summary']
            prompt = (
            f"책 제목: {title}\n"
            f"추천 이유: '{book_title}'과 유사한 줄거리를 가지고 있습니다. "
            f"두 책이 어떤 점에서 비슷한지 간단히 설명해 주세요.\n\n"
            f" **주의사항:**\n"
            f"- **결말, 반전, 주요 사건의 결과**를 절대 언급하지 마세요.\n"
            f"- 오직 책의 **설정, 등장인물의 특징, 분위기, 주제**만 설명하세요.\n"
            f"- 독자가 직접 책을 읽고 경험할 수 있도록 궁금증을 유발하는 방식으로 서술하세요.\n\n"
            f"'{book_title}' 요약: {dt[dt['Book title'] == book_title].iloc[0]['Summarized Plot Summary']}\n"
            f"'{title}' 요약: {summarized_plot}\n\n"
        )
            futures.append(executor.submit(chatgpt_generate, prompt))
        for future in concurrent.futures.as_completed(futures):
            explanations.append(future.result())
    return explanations

# Streamlit app
st.title("Book Recommendation System")
st.write("Enter a book title to get recommendations based on plot similarity!")

# User input
book_title = st.text_input("Enter Book Title:")

# Number of recommendations
top_n = st.slider("Number of Recommendations", min_value=1, max_value=5, value=3)

# Faiss 인덱스를 생성하는 함수
def create_faiss_index():
    # 데이터셋의 모든 임베딩 벡터를 float32로 변환
    embeddings = np.vstack(dt['Summarized Plot Embedding'].tolist()).astype('float32')
    # 내적(Inner Product) 기반의 Faiss 인덱스 생성
    index = faiss.IndexFlatIP(embeddings.shape[1])
    # 인덱스에 모든 벡터 추가
    index.add(embeddings)
    return index, embeddings

# Faiss 인덱스 생성
faiss_index, embeddings = create_faiss_index()

# Faiss 기반 추천 함수
def recommend_books_with_faiss(book_title, top_n=3):
    # 입력한 책 제목으로 해당 책의 임베딩 검색
    selected_books = dt[dt['Book title'].str.lower() == book_title.lower()]
    if selected_books.empty:
        return []

    # 선택된 책의 임베딩 추출 및 정규화
    selected_embedding = np.array(selected_books.iloc[0]['Summarized Plot Embedding']).astype('float32').reshape(1, -1)
    selected_embedding /= np.linalg.norm(selected_embedding)  # 정규화

    # Faiss 인덱스를 사용하여 최근접 이웃 검색
    distances, indices = faiss_index.search(selected_embedding, top_n + 1)  # +1은 자기 자신 포함
    recommendations = []

    for idx, dist in zip(indices[0], distances[0]):
        title = dt.iloc[idx]['Book title']
        if title.lower() != book_title.lower():  # 자기 자신 제외
            recommendations.append((title, dist))  # 책 제목과 유사도 추가

    return recommendations

if st.button("Recommend"):
    if book_title.strip() == "":
        st.warning("Please enter a valid book title.")
    else:
        recommendations = recommend_books_with_faiss(book_title, top_n=top_n)

        if not recommendations:  # 추천 결과가 없는 경우
            st.error(f"No recommendations found for '{book_title}'. Please try another book.")
        else:
            st.success(f"Top {top_n} recommendations for '{book_title}':")
            explanations = generate_explanations(recommendations, book_title)
            for i, ((title, similarity), explanation) in enumerate(zip(recommendations, explanations), 1):
                st.subheader(f"{i}. {title} (Similarity: {similarity:.4f})")
                st.write(f"**Reason:** {explanation}")

