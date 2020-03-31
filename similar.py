from scipy import spatial

#cosine similarity of two vectors
def cos_sim(vec1,vec2):
	return 1-spatial.distance.cosine(vec1,vec2)

#find most similar word given word vector
def sim_words_from_vec(vocab,word_vec):
	#prob controls number of queries to search. -15=32k, -18=147k, -20=563k.
	queries = [w for w in vocab if w.is_lower and w.prob >= -16]
	by_similarity = sorted(queries, key=lambda w: cos_sim(w.vector,word_vec), reverse=True)
	sim_tokens = by_similarity[:10]
	return [token.text for token in sim_tokens]
