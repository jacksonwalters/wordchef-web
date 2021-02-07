import spacy, numpy, random, pickle, pandas, sys
import sklearn.neighbors as nbs

MIN_PROB = 1e-6

#as of spaCy v3.0, word probabilities require spacy-lookup-data
#instead, using freq. table from Kaggle - https://www.kaggle.com/rtatman/english-word-frequency
print("Loading word frequency table...")
df = pandas.read_csv("unigram_freq.csv", usecols=['word', 'count'])
prob_table = dict(zip(df["word"],df["count"]/max(df["count"])))
def prob(word):
	try:
		return prob_table[word]
	except KeyError:
		return 0

#load NLP tool spaCy
print("Loading spaCy...")
nlp=spacy.load("en_core_web_lg")
print("spaCy loaded.")

#get plaintext words as list from spacy vocab. ensure they have wordvector, are lowercase, and aren't too rare
print("Total number of words=",len(nlp.vocab.strings))
print("Getting words...")
words = [word for word in nlp.vocab.strings if nlp.vocab.has_vector(word) and word.islower() and prob(word) >= MIN_PROB]
print("Retrieved ",len(words),"words with vectors.")

#get wordvectors for all words as numpy array
print("Total number of wordvectors=",len(nlp.vocab.vectors))
print("Getting wordvectors...")
wordvecs = numpy.array([nlp.vocab.get_vector(word) for word in words])
print("Retrieved=",len(wordvecs),"wordvectors.")

#ensure the list of words corresponds to the list of wordvectors
assert len(words) == len(wordvecs)
spot_check = random.choice(range(0,len(words)))
assert numpy.array_equal(nlp(words[spot_check]).vector,wordvecs[spot_check])
print("Spot check passed.")

#pickle the entire vocab
with open('words.pkl', 'wb') as f:
		pickle.dump(words,f,protocol=pickle.HIGHEST_PROTOCOL)
print("Dumped vocab words to pickle file vocab.pkl")

#place all wordvectors in balltree, and pickle entire tree
tree = nbs.BallTree(wordvecs)
with open('balltree.pkl', 'wb') as f:
		pickle.dump(tree,f,protocol=pickle.HIGHEST_PROTOCOL)
print("Dumped wordvector BallTree to pickle file balltree.pkl")

#place all wordvectors in balltree, and pickle entire tree
dict = dict(zip(words,wordvecs))
with open('dict.pkl', 'wb') as f:
		pickle.dump(dict,f,protocol=pickle.HIGHEST_PROTOCOL)
print("Dumped word2vec dictionary in dict.pkl")
