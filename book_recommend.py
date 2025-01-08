import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
import multiprocessing as mp
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)
import nltk
nltk.download('stopwords', quiet=True)
def preprocess_text(text):
    # lowercasing
    lowercased_text = text.lower()

    # cleaning 
    import re 
    remove_punctuation = re.sub(r'[^\w\s]', '', lowercased_text)
    remove_white_space = remove_punctuation.strip()

    # Tokenization = Breaking down each sentence into an array
    from nltk.tokenize import word_tokenize
    tokenized_text = word_tokenize(remove_white_space)

    # Stop Words/filtering = Removing irrelevant words
    from nltk.corpus import stopwords
    stopwords = set(stopwords.words('english'))
    stopwords_removed = [word for word in tokenized_text if word not in stopwords]

    # Stemming = Transforming words into their base form
    from nltk.stem import PorterStemmer
    ps = PorterStemmer()
    stemmed_text = [ps.stem(word) for word in stopwords_removed]
    
    # Putting all the results into a dataframe.
    df = pd.DataFrame({
        'DOCUMENT': [text],
        'LOWERCASE' : [lowercased_text],
        'CLEANING': [remove_white_space],
        'TOKENIZATION': [tokenized_text],
        'STOP-WORDS': [stopwords_removed],
        'STEMMING': [stemmed_text]
    })

    return df
def calculate_tfidf(corpus):
    # Call the preprocessing result
    df = preprocessing(corpus)
        
    # Make each array row from stopwords_removed to be a sentence
    stemming = corpus['STEMMING'].apply(' '.join)
    
    # Count TF-IDF
    from sklearn.feature_extraction.text import TfidfVectorizer
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(stemming)
    
    # Get words from stopwords array to use as headers
    feature_names = vectorizer.get_feature_names_out()

    # Combine header titles and weights
    df_tfidf = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names)
    df_tfidf = pd.concat([df, df_tfidf], axis=1)

    return df_tfidf
def cosineSimilarity(corpus):
    # Call the TF-IDF result
    df_tfidf = calculate_tfidf(corpus)
    
    # Get the TF-IDF vector for the first item (index 0)
    vector1 = df_tfidf.iloc[0, 6:].values.reshape(1, -1)

    # Get the TF-IDF vector for all items except the first item
    vectors = df_tfidf.iloc[:, 6:].values
    
    # Calculate cosine similarity between the first item and all other items
    from sklearn.metrics.pairwise import cosine_similarity
    cosim = cosine_similarity(vector1, vectors)
    cosim = pd.DataFrame(cosim)
    
    # Convert the DataFrame into a one-dimensional array
    cosim = cosim.values.flatten()

    # Convert the cosine similarity result into a DataFrame
    df_cosim = pd.DataFrame(cosim, columns=['COSIM'])

    # Combine the TF-IDF array with the cosine similarity result
    df_cosim = pd.concat([df_tfidf, df_cosim], axis=1)

    return df_cosim
import pandas as pd


# Define the column names
column_names = [
    'Wikipedia article ID', 
    'Freebase ID', 
    'Book title', 
    'Author', 
    'Publication date', 
    'Book genres (Freebase ID:name tuples)', 
    'Plot summary'
]
  

# Read the .txt file into a DataFrame
df = pd.read_csv('data/booksummaries.txt', delimiter='\t', names=column_names, header=None)  # Adjust delimiter as needed

# Save the DataFrame to a .csv file with column names
df.to_csv('output.csv', index=False)
file_path='output.csv'
df = pd.read_csv(file_path)
from sklearn.feature_extraction.text import TfidfVectorizer

# Initialize the TF-IDF Vectorizer
tfidf_vectorizer = TfidfVectorizer()

# Apply TF-IDF on the 'Plot summary' column
tfidf_matrix = tfidf_vectorizer.fit_transform(df['Plot summary'])

# Show the shape of the resulting TF-IDF matrix
print(tfidf_matrix.shape)
from sklearn.metrics.pairwise import cosine_similarity

# Calculate the cosine similarity matrix
cosine_sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Show the resulting similarity matrix
print(cosine_sim_matrix)
def recommend_books(book_title, df, cosine_sim_matrix, top_n=5):
    # Reset the index of the DataFrame and create a reverse mapping of indices and book titles
    df = df.reset_index()
    indices = pd.Series(df.index, index=df['Book title']).drop_duplicates()
    
    # Check if the book exists in the dataset
    if book_title not in indices:
        print(f"Book titled '{book_title}' not found in the dataset.")
        return []
    
    # Get the index of the book that matches the title
    idx = indices[book_title]
    
    # Get the pairwise similarity scores of all books with that book
    sim_scores = list(enumerate(cosine_sim_matrix[idx]))
    
    # Sort the books based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Skip the first book (itself) and get the scores of the top_n most similar books
    sim_scores = sim_scores[1:top_n+1]
    
    # Get the book indices
    book_indices = [i[0] for i in sim_scores]
    
    # Return the top_n most similar books
    return df['Book title'].iloc[book_indices].tolist()
# Example usage:
book_to_recommend = "Book of Joshua"
recommended_books = recommend_books(book_to_recommend, df, cosine_sim_matrix, top_n=5)

print(f"Books similar to '{book_to_recommend}':")
for idx, title in enumerate(recommended_books, 1):
    print(f"{idx}. {title}")