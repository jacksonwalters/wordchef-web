# wordchef
Flask+Gunicorn+nginx webapp to take linear combinations of words.

Uses spaCy to generate full vocab and corresponding wordvectors. Wordvectors are stored in BallTrees (neighbors.sklearn). Files are split into small pieces and pickled for storage.
