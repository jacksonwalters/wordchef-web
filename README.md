#wordchef

PHP + pgSQL + pgvector webapp to take linear combinations of words

- Uses spaCy to generate full vocab and corresponding wordvectors
- Wordvectors are stored in a pgvector database in PostgreSQL which allows fast semantic search
- Given two words, look up their wordcvectors and take the average
- Find the nearest five words to the averaged vector
