#perform doc2vec embeddings on comments with gensim
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize

import nltk
print(nltk.data.path)

print("Loading model...")

model = Doc2Vec.load("d2v.model")
print("Model loaded, proceeding to inference...")

# Test data
try:
    test_data = word_tokenize("hello how are you".lower())
    print(f"Tokenized test data: {test_data}")
except Exception as e:
    print(f"Error during tokenization: {e}")

# Load the model and infer vector
try:
    v1 = model.infer_vector(test_data)
    print(f"Inferred docvector for 'hello how are you': {v1}")
except Exception as e:
    print(f"Error during vector inference: {e}")

# Get most similar docvectors
try:
    most_similar = model.dv.most_similar('1')
    print(f"Most similar docvectors to '1': {most_similar}")
except Exception as e:
    print(f"Error fetching most similar docvectors: {e}")

# Fetch specific docvector
try:
    docvector = model.dv['1']
    print(f"Docvector of '1': {docvector}")
except Exception as e:
    print(f"Error fetching docvector for '1': {e}")
