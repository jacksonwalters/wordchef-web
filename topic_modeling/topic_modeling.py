#perform doc2vec embeddings on comments with gensim
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize

print("beginning topic modeling script...")

import os

model_path = "d2v.model"
if not os.path.exists(model_path):
    print(f"Model file not found: {model_path}")
else:
    print(f"Model file found: {model_path}")

try:
    model = Doc2Vec.load("d2v.model")
except Exception as e:
    print(f"Error loading model: {e}")
    exit(1)  # Exit with an error code

# Check after model loading
print("Model seems to be loaded, continuing...")


#to find the vector of a document which is not in training data
test_data = word_tokenize("hello how are you".lower())
v1 = model.infer_vector(test_data)

print("inferred docvector for 'hello how are you': ", v1)
print("most similar docvectors to '1': ",model.dv.most_similar('1'))
print("docvector of '1': ",model.dv['1'])