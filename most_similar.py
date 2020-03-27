#find words similar/close to wordvector
def most_similar(word,word_vec):
	queries = [w for w in word.vocab if w.is_lower == word.is_lower and w.prob >= -15]
	by_similarity = sorted(queries, key=lambda w: word.similarity(w), reverse=True)
	return by_similarity[:10]
