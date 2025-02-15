import numpy as np
import faiss

class BookRecommender:
    def __init__(self, dt):
        self.dt = dt
        self.faiss_index, self.embeddings = self.create_faiss_index()

    def create_faiss_index(self):
        embeddings = np.vstack(self.dt['Summarized Plot Embedding'].tolist()).astype('float32')
        index = faiss.IndexFlatIP(embeddings.shape[1])  # 내적 기반 Faiss 인덱스
        index.add(embeddings)
        return index, embeddings

    def recommend_books(self, book_title, top_n=3):
        selected_books = self.dt[self.dt['Book title'].str.lower() == book_title.lower()]
        if selected_books.empty:
            return []
        
        selected_embedding = np.array(selected_books.iloc[0]['Summarized Plot Embedding']).astype('float32').reshape(1, -1)
        selected_embedding /= np.linalg.norm(selected_embedding)  # 정규화

        distances, indices = self.faiss_index.search(selected_embedding, top_n + 1)  # 자기 자신 포함
        recommendations = [(self.dt.iloc[idx]['Book title'], dist) for idx, dist in zip(indices[0], distances[0]) if self.dt.iloc[idx]['Book title'].lower() != book_title.lower()]
        return recommendations
