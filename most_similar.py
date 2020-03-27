from scipy import spatial

#cosine similarity of two vectors
def cos_sim(vec1,vec2):
	return 1-spatial.distance.cosine(vec1,vec2)

#find most similar word given word vector
def most_similar(word_vec):
	queries = [w for w in nlp.vocab if w.is_lower and w.prob >= -15]
	by_similarity = sorted(queries, key=lambda w: cos_sim(w.vector,word_vec), reverse=True)
	return by_similarity[:10]
