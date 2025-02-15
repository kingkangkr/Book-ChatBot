import os
import concurrent.futures
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chatgpt_generate(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating explanation: {e}"

def generate_explanations(recommendations, book_title, dt):
    explanations = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        # 🔹 책 제목이 데이터프레임에 존재하는지 먼저 확인
        book_data = dt[dt['Book title'].str.lower() == book_title.lower()]
        if book_data.empty:
            return [f"Error: Book title '{book_title}' not found in dataset."]

        # 🔹 book_title이 존재하면 요약을 가져옴
        summarized_plot = book_data.iloc[0]['Summarized Plot Summary']

        for title, _ in recommendations:
            recommended_book_data = dt[dt['Book title'] == title]
            if recommended_book_data.empty:
                explanations.append(f"Error: Summary for '{title}' not found.")
                continue

            recommended_plot = recommended_book_data.iloc[0]['Summarized Plot Summary']

            prompt = (
                f"책 제목: {title}\n"
                f"추천 이유: '{book_title}'과 유사한 줄거리를 가지고 있습니다. "
                f"두 책이 어떤 점에서 비슷한지 간단히 설명해 주세요.\n\n"
                f" **주의사항:**\n"
                f"- **결말, 반전, 주요 사건의 결과**를 절대 언급하지 마세요.\n"
                f"- 오직 책의 **설정, 등장인물의 특징, 분위기, 주제**만 설명하세요.\n"
                f"- 독자가 직접 책을 읽고 경험할 수 있도록 궁금증을 유발하는 방식으로 서술하세요.\n\n"
                f"'{book_title}' 요약: {summarized_plot}\n"
                f"'{title}' 요약: {recommended_plot}\n\n"
            )
            futures.append(executor.submit(chatgpt_generate, prompt))

        for future in concurrent.futures.as_completed(futures):
            explanations.append(future.result())

    return explanations
