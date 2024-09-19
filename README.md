**wordchef**

PHP + pgSQL + pgvector webapp to take linear combinations of words

- Uses spaCy to generate full vocab and corresponding wordvectors
- Wordvectors are stored in a PostgreSQL database with pgvector which allows fast semantic search
- Given two words, look up their wordcvectors and take the average
- Find the nearest five words to the averaged vector

**TOPIC MODELING**

Available at https://wordchef.app/topic_modeling. 

Built from https://github.com/jacksonwalters/nlp/topic_modeling

- User uploads comments .csv and keywords .csv
- Load pre-trained gensim doc2vec model
- Embed comments as docs to get vector embeddings
- Use k-means to cluster comments into groups
- Compute TF-IDF scores across clusters
- Embed keywords/bigrams and compute nearest bigram to cluster centroid
- Find nearest keyword/bigram to each comment
