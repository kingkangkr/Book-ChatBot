"""
이 스크립트는 다운로드된 책 요약 PDF 파일에서 데이터를 추출하여 CSV 파일로 저장하는 역할을 합니다.
- 책 제목, 저자 이름, 요약본(Short Summary), 장르 정보를 수집합니다.
- PyPDF2를 사용하여 PDF에서 텍스트를 추출합니다.
- OpenAI API를 활용하여 책의 장르를 자동 분류합니다.
"""

import os
import re
import csv
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from openai import OpenAI

# 환경 변수 로드
load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def extract_text_from_pdf(file_path):
    """
    주어진 PDF 파일에서 텍스트를 추출합니다.
    :param file_path: PDF 파일의 경로
    :return: 추출된 텍스트 문자열
    """
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_book_name(file_path):
    """
    PDF 파일 이름에서 책 제목을 추출합니다.
    (예: "(aaa)(bbb)책 제목.pdf" → "책 제목" 추출)
    :param file_path: PDF 파일의 경로
    :return: 추출된 책 제목 문자열
    """
    file_name = os.path.basename(file_path)
    file_name = re.sub(r"\.pdf$", "", file_name)
    return file_name.split(")")[-1].strip() if ")" in file_name else file_name

def extract_short_summary(pdf_text, book_name):
    """
    PDF에서 'Short Summary' 섹션을 추출합니다.
    :param pdf_text: 추출된 PDF 텍스트
    :param book_name: 책 제목
    :return: 정제된 Short Summary 문자열
    """
    pattern = r"▣ Short Summary\s+(.*?)(?=▣ 차례)"
    match = re.search(pattern, pdf_text, re.DOTALL)
    if match:
        short_summary = re.sub(rf"- \d+ -\s*{re.escape(book_name)}", "", match.group(1).strip(), flags=re.DOTALL)
        return re.sub(r"\s{2,}", " ", short_summary).strip()
    return None

def extract_author_name(pdf_text):
    """
    PDF에서 저자 이름을 추출합니다.
    :param pdf_text: 추출된 PDF 텍스트
    :return: 저자 이름 문자열
    """
    match = re.search(r"▣ 저자\s+(.+?)\n", pdf_text, re.DOTALL)
    return re.sub(r"\s{2,}", " ", match.group(1).strip()) if match else None

def extract_genres(plot_summary):
    """
    OpenAI API를 사용하여 책의 장르를 자동 추출합니다.
    :param plot_summary: 책의 요약 내용
    :return: 최대 3개의 장르 리스트
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "책 요약을 기반으로 최대 3개의 장르를 한글로 추출하세요."},
                {"role": "user", "content": f"{plot_summary}"}
            ]
        )
        return [genre.strip() for genre in response.choices[0].message.content.split(",")][:3]
    except Exception as e:
        print(f"OpenAI API 오류: {e}")
        return []

def append_to_csv(file_name, column_names, data):
    """
    책 데이터를 CSV 파일에 추가합니다.
    :param file_name: CSV 파일 이름
    :param column_names: CSV 컬럼 리스트
    :param data: 저장할 책 데이터 (딕셔너리)
    """
    file_exists = os.path.isfile(file_name)
    with open(file_name, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=column_names)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

if __name__ == "__main__":
    # CSV 파일 및 컬럼 설정
    csv_file_name = "books.csv"
    columns = ["Book title", "Author", "Book genres", "Plot summary"]

    # 다운로드 폴더의 모든 PDF 처리
    download_folder = os.path.join(os.getcwd(), "download")
    downloaded_files = [f for f in os.listdir(download_folder) if f.endswith(".pdf")]

    for file_name in downloaded_files:
        file_path = os.path.join(download_folder, file_name)
        book_title = extract_book_name(file_path)
        pdf_text = extract_text_from_pdf(file_path)
        plot_summary = extract_short_summary(pdf_text, book_title)
        author_name = extract_author_name(pdf_text)

        if plot_summary and author_name:
            genres = ", ".join(extract_genres(plot_summary))
            book_data = {"Book title": book_title, "Author": author_name, "Book genres": genres, "Plot summary": plot_summary}
            append_to_csv(csv_file_name, columns, book_data)
        else:
            print(f"{file_name}에서 필요한 정보를 추출하지 못했습니다.")
