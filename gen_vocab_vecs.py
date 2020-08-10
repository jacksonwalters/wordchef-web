import spacy
import numpy
import sklearn.neighbors as nbs
import pickle
import random

print("Loading spaCy...")
nlp=spacy.load("en_core_web_lg")
print("spaCy loaded.")

#get plaintext words as list from spacy vocab. ensure they have wordvector, are lowercase, and aren't too rare
#{prob:# words} ~ {-15:32k, -16:50k, -17:77k, -18:147k, -19:183k, -20:302k} 
words = [w.text for w in nlp.vocab if w.is_lower and w.prob >= -20 and w.has_vector]

#get wordvectors for all words as numpy array
wordvecs = numpy.array([w.vector for w in nlp.vocab if w.is_lower and w.prob >= -20 and w.has_vector])

#ensure the list of words corresponds to the list of wordvectors
assert len(words) == len(wordvecs)
spot_check = random.choice(range(0,len(words)))
assert numpy.array_equal(nlp(words[spot_check]).vector,wordvecs[spot_check])

#split words into separate files of ~22k words/wordvectors each
#~17 bytes/word, as each word is at most ~17 characters
#~1.2 mB/vector, as each vector is 300 rational numbers
num_files = 7
file_len = len(words)//num_files
for i in range(0,num_files):
	words_i = words[i*file_len:(i+1)*file_len]
	wordvecs_i = wordvecs[i*file_len:(i+1)*file_len]
	tree_i = nbs.BallTree(wordvecs_i)
	with open('words_'+str(i)+'.pkl', 'wb') as f:
		pickle.dump(words_i,f,protocol=pickle.HIGHEST_PROTOCOL)
	with open('wordvecs_'+str(i)+'.pkl', 'wb') as f:
		pickle.dump(wordvecs_i,f,protocol=pickle.HIGHEST_PROTOCOL)
	
#if number of files does not evenly divide file length, append final file
if len(words) % num_files != 0:
	last_ind = num_files+1
	last_words = words[num_files*file_len:num_files*file_len+len(words)%num_files]
	last_wordvecs = wordvecs[num_files*file_len:num_files*file_len+len(words)%num_files]
	with open('words_'+str(last_ind)+'.pkl', 'wb') as f:
		pickle.dump(last_words,f,protocol=pickle.HIGHEST_PROTOCOL)
	with open('wordvecs_'+str(last_ind)+'.pkl', 'wb') as f:
		pickle.dump(last_wordvecs,f,protocol=pickle.HIGHEST_PROTOCOL)
	
	
	

