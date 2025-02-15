import streamlit as st
from src.data_loader import load_data
from src.recommender import BookRecommender
from src.chatbot import generate_explanations

def run_app():
    """ Streamlit 앱 실행 함수 """
    st.title("Book Recommendation System")
    st.write("Enter a book title to get recommendations based on plot similarity!")

    # 데이터 로드
    dt = load_data()
    recommender = BookRecommender(dt)

    # 사용자 입력
    book_title = st.text_input("Enter Book Title:")
    top_n = st.slider("Number of Recommendations", min_value=1, max_value=5, value=3)

    if st.button("Recommend"):
        if book_title.strip() == "":
            st.warning("Please enter a valid book title.")
        else:
            recommendations = recommender.recommend_books(book_title, top_n=top_n)

            if not recommendations:
                st.error(f"No recommendations found for '{book_title}'. Please try another book.")
            else:
                st.success(f"Top {top_n} recommendations for '{book_title}':")
                explanations = generate_explanations(recommendations, book_title, dt)
                for i, ((title, similarity), explanation) in enumerate(zip(recommendations, explanations), 1):
                    st.subheader(f"{i}. {title} (Similarity: {similarity:.4f})")
                    st.write(f"**Reason:** {explanation}")

if __name__ == "__main__":
    run_app()
