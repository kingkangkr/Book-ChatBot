import pandas as pd
import ast
import streamlit as st
import os
@st.cache_data
def load_data():
    # 현재 파일(data_loader.py)의 경로를 기준으로 상위 폴더의 'data/' 디렉토리 찾기
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "filtered_booksummaries.csv")

    # 파일 존재 여부 확인 (문제가 발생하면 오류 출력)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")
    print(f"Loading data from: {file_path}")  # 경로 확인용 디버깅 코드
    dt = pd.read_csv(file_path)
    print("Data loaded successfully!")  # 디버깅 로그 추가
    dt['Summarized Plot Embedding'] = dt['Summarized Plot Embedding'].apply(ast.literal_eval)
    return dt
