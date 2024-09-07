import spacy, numpy, random, pickle, pandas, sys
import sklearn.neighbors as nbs
from spacy.lookups import load_lookups


MIN_PROB = -18

#load NLP tool spaCy
print("Loading spaCy...")
nlp=spacy.load("en_core_web_lg")
print("spaCy loaded.")

#load lexeme probability table
lookups = load_lookups("en", ["lexeme_prob"])
nlp.vocab.lookups.add_table("lexeme_prob", lookups.get_table("lexeme_prob"))

#get plaintext words as list from spacy vocab. ensure they have wordvector, are lowercase, and aren't too rare
print("Total number of words in spaCy vocab=",len(nlp.vocab.strings))
print("Getting words...")
words = [word for word in nlp.vocab.strings if nlp.vocab.has_vector(word) and word.islower() and nlp.vocab[word].prob >= MIN_PROB]
print("Retrieved ",len(words),"lowercase words with vectors and prob >=",MIN_PROB)

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
#pickle.HIGHEST_PROTOCOL depends on Python version
with open('vocab.pkl', 'wb') as f:
		pickle.dump(words,f,protocol=4)
print("Dumped vocab words to pickle file vocab.pkl")

#place all wordvectors in balltree, and pickle entire tree
tree = nbs.BallTree(wordvecs)
with open('balltree.pkl', 'wb') as f:
		pickle.dump(tree,f,protocol=4)
print("Dumped wordvector BallTree to pickle file balltree.pkl")

#create word:vector dict and pickle it
dict = dict(zip(words,wordvecs))
with open('dict.pkl', 'wb') as f:
		pickle.dump(dict,f,protocol=4)
print("Dumped word2vec dictionary in dict.pkl")
