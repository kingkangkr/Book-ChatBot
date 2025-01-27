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

# API 사용량 추적
api_usage_tokens = 0

def extract_text_from_pdf(file_path):
    """
    Extract text from a given PDF file.
    :param file_path: Path to the PDF file.
    :return: Extracted text from the PDF.
    """
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_book_name(file_path):
    """
    Extract the book title from the PDF file name.
    Assumes the format "(aaa)(bbb)책 제목.pdf" or similar.
    :param file_path: Path to the PDF file.
    :return: Extracted book title.
    """
    file_name = os.path.basename(file_path)

    # Remove the file extension
    file_name = re.sub(r"\.pdf$", "", file_name)

    # Extract the part after the last closing parenthesis
    if ")" in file_name:
        book_title = file_name.split(")")[-1].strip()
    else:
        book_title = file_name  # If no parentheses, use the full file name

    return book_title

def extract_short_summary(pdf_text, book_name):
    """
    Extract the Short Summary section from the PDF text.
    :param pdf_text: The text extracted from the PDF.
    :param book_name: The book title.
    :return: Cleaned short summary text.
    """
    pattern = r"▣ Short Summary\s+(.*?)(?=▣ 차례)"
    match = re.search(pattern, pdf_text, re.DOTALL)

    if match:
        short_summary = match.group(1).strip()

        # Remove page footers like "- N - Book Name"
        cleaned_summary = re.sub(rf"- \d+ -\s*{re.escape(book_name)}", "", short_summary, flags=re.DOTALL)

        # Additional cleaning
        cleaned_summary = re.sub(r"- \d+ -.*?\s", " ", cleaned_summary, flags=re.DOTALL)
        cleaned_summary = re.sub(r"\n+", " ", cleaned_summary)
        cleaned_summary = re.sub(r"\s{2,}", " ", cleaned_summary).strip()

        return cleaned_summary
    else:
        return None

def extract_author_name(pdf_text):
    """
    Extract the author name from the PDF text.
    :param pdf_text: The text extracted from the PDF.
    :return: Author name.
    """
    author_name_pattern = r"▣ 저자\s+(.+?)\n"
    match = re.search(author_name_pattern, pdf_text, re.DOTALL)

    if match:
        author_name = match.group(1).strip()
        return re.sub(r"\s{2,}", " ", author_name)  # Clean up spaces
    return None

def extract_genres(plot_summary):
    """
    Use OpenAI API to extract genres from the book summary.
    :param plot_summary: Plot summary of the book.
    :return: List of genres (up to 3).
    """
    global api_usage_tokens
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts genres from book summaries."},
                {"role": "user", "content": f"당신은 following plot summary를 읽고 3개의 장르를 추출하세요. 장르는 한글로 세가지를 연속으로 출력하도록 합니다. 예를 들어 '의학, 사회, 자기계발' 과 같이 쉼표와 띄어쓰기로 구분합니다.\n{plot_summary}"}
            ]
        )
        # Track API usage tokens
        api_usage_tokens += response.usage.total_tokens

        # Parse the response content for genres
        genres = response.choices[0].message.content
        return [genre.strip() for genre in genres.split(",")][:3]
    except Exception as e:
        print(f"ChatGPT API 호출 중 오류가 발생했습니다: {e}")
        return []

def append_to_csv(file_name, column_names, data):
    """
    Append data to a CSV file.
    :param file_name: CSV file name.
    :param column_names: List of column names.
    :param data: Data to append (as a dictionary).
    """
    file_exists = os.path.isfile(file_name)
    with open(file_name, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=column_names)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

# CSV 파일 및 컬럼 설정
csv_file_name = "books.csv"
columns = ["Book title", "Author", "Book genres", "Plot summary"]

# 다운로드 폴더의 모든 PDF 처리
current_directory = os.getcwd()
download_folder = os.path.join(current_directory, "download")

downloaded_files = [f for f in os.listdir(download_folder) if f.endswith(".pdf")]

for file_name in downloaded_files:
    file_path = os.path.join(download_folder, file_name)

    # 책 제목 추출
    book_title = extract_book_name(file_path)

    # PDF 텍스트 추출
    pdf_text = extract_text_from_pdf(file_path)

    # Short Summary 추출
    plot_summary = extract_short_summary(pdf_text, book_title)

    # 저자 이름 추출
    author_name = extract_author_name(pdf_text)

    if plot_summary and author_name:
        # OpenAI API를 사용하여 장르 추출
        genres = extract_genres(plot_summary)
        genres_str = ", ".join(genres)  # Join genres into a single string

        # 데이터를 CSV에 추가
        book_data = {
            "Book title": book_title,
            "Author": author_name,
            "Book genres": genres_str,
            "Plot summary": plot_summary
        }
        append_to_csv(csv_file_name, columns, book_data)

    else:
        print(f"{file_name}에서 필요한 정보를 모두 추출하지 못했습니다.")

# 총 사용한 API 토큰 및 비용 출력
token_cost_per_1k = 0.002  # gpt-3.5-turbo 비용 ($0.002 per 1k tokens)
total_cost = (api_usage_tokens / 1000) * token_cost_per_1k
print(f"총 사용한 API 토큰: {api_usage_tokens}")
print(f"예상 비용: ${total_cost:.4f}")
