from scipy import spatial
import numpy as np

#find most similar word given word vector
#use either cosine similarity (reverse=True) or euclidean dist.
def sim_words_from_vec(queries,word_vec):
	#must use euc_dist if word_vec is all zeros
	dist = spatial.distance.cosine if np.any(word_vec) else spatial.distance.euclidean
	by_similarity = sorted(queries, key=lambda w: dist(w.vector,word_vec))
	sim_tokens = by_similarity[:10]
	return [token.text for token in sim_tokens]
