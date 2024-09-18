#perform doc2vec embeddings on comments with gensim
import numpy as np
import pandas as pd
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
from sklearn.cluster import KMeans

print("Loading data...<br>")

#read in the data
n_samples = 1000
data = pd.read_csv('uploads/comments.csv',header=None,names=['comment'])
comments = data['comment'][:n_samples]

keywords = list(pd.read_csv("uploads/keywords.csv"))

print("First 10 Keywords:", keywords[:10],"<br>")

try:
    model = Doc2Vec.load("d2v.model")
    print("Model loaded successfully.<br>")
except FileNotFoundError:
    print("Model file not found. Please check the file path.")
except Exception as e:
    print(f"An error occurred: {e}")

comment_vectors = {doc:model.infer_vector(word_tokenize(doc.lower())) for doc in comments}
comment_vectors_list = list(comment_vectors.values())

keyword_vectors = {doc:model.infer_vector(word_tokenize(doc.lower())) for doc in keywords}
keyword_vectors_list = list(keyword_vectors.values())

#determine the number of clusters with elbow method, ideally automatically
num_clusters = 5

try:
    # Attempt to create and fit the KMeans model
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(comment_vectors_list)
    print("KMeans model fitted successfully.<br>")
except ValueError as ve:
    print(f"ValueError: {ve}")  # Handle issues with data shape or invalid parameters
except NotFittedError:
    print("Error: The model was not fitted.<br>")
except Exception as e:
    print(f"An unexpected error occurred: {e}<br>")

#define cosine similarity
from numpy.linalg import norm
def cosine_similarity(v,w):
    return np.dot(v,w)/(norm(v)*norm(w))

#find closest bigram to centroid
centroids  = kmeans.cluster_centers_
nearest_keyword_to_centroid = []
for centroid in centroids:
    min_dist = 2**32
    nearest_keyword = ""
    for keyword, embedding in keyword_vectors.items():
        #dist = cosine_similarity(centroid, embedding)
        dist = np.linalg.norm(centroid - embedding)
        if dist < min_dist:
            min_dist = dist
            nearest_keyword = keyword
    nearest_keyword_to_centroid.append((nearest_keyword,min_dist))

print("Nearest keyword to centroid:<br>")
for nearest_keyword in nearest_keyword_to_centroid:
    print(nearest_keyword,"<br>")
print("<br>")

#find the keyword which is closest to each comment in the embedding
nearest_keyword_to_comment = []
for comment in comments[:10]:
    min_dist = 2**32
    nearest_keyword = ""
    comment_vec = comment_vectors[comment]
    for keyword, embedding in keyword_vectors.items():
        #dist = cosine_similarity(comment_vec, embedding)
        dist = np.linalg.norm(comment_vec - embedding)
        if dist < min_dist:
            min_dist = dist
            nearest_keyword = keyword
    nearest_keyword_to_comment.append((comment,nearest_keyword,min_dist))

print("Nearest keyword to comment:<br>")
for nearest_comment in nearest_keyword_to_comment:
    print(nearest_comment,"<br>")


