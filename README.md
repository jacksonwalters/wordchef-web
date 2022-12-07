#wordchef
Flask+Gunicorn+nginx webapp to take linear combinations of words.

Uses spaCy to generate full vocab and corresponding wordvectors. Wordvectors are stored in space-partitioning BallTrees (neighbors.sklearn) for fast reverse lookup. Files pickled for storage.
