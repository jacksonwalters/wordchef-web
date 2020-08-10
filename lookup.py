import numpy
import sklearn
import pickle

#compute linear combination amounts*vec(words). find nearest neighbor words.
def nearest_words(amounts,words):
	#load {word:vector} dictionary from pickle
	with open('dict.pkl') as f:
		to_vec = pickle.load(f)

	#get vectors for all words
	vecs=[]
	for word in words:
		try:
			vec = to_vec[word]
			vecs.append(vec)
		#if word is not in vocab, do not include
		except KeyError:
			vecs.append(numpy.zeros(300))
	
	#clear dictionary from memory
	to_vec = None

	#compute linear combination of user wordvectors
	assert len(vecs) == len(amounts)
	n = len(vecs)
	lin_comb = numpy.zeros(300)
	for i in range(n):
		lin_comb += amounts[i]*vecs[i]
	
	#load wordvector balltree from pickle file 
	with open('balltree.pkl') as f:
		tree = pickle.load(f)
	
	#perform nearest neighbor search of wordvector vocabulary
	dist, ind = tree.query([lin_comb],5)
	
	#clear tree from memory
	tree = None

	#load vocab from pickle file
	with open('words.pkl') as f:
		vocab = pickle.load(f)
	
	#lookup nearest words using indices from tree
	near_words = [vocab[i] for i in ind[0]]
	
	#clear vocab from memory
	vocab = None

	return near_words
	
	
	
