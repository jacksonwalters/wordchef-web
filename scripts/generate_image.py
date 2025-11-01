#!/usr/bin/env python3
import sys
import numpy as np
from PIL import Image
import io, base64

if len(sys.argv) != 3:
    print("Usage: python3 vector_image.py <embedding_csv> <word>")
    sys.exit(1)

embedding_csv = sys.argv[1]
word = sys.argv[2]

# Parse vector
embedding = np.array([float(x) for x in embedding_csv.split(',')], dtype=float)

# Fixed rectangular dimensions
WIDTH, HEIGHT = 15, 20
SCALE = 20  # how much to enlarge each pixel

# Pad or trim to fit 15x20
total_size = WIDTH * HEIGHT
if embedding.size < total_size:
    embedding = np.pad(embedding, (0, total_size - embedding.size))
elif embedding.size > total_size:
    embedding = embedding[:total_size]

arr = embedding.reshape((HEIGHT, WIDTH))

# Normalize to [0, 255]
arr_min, arr_max = arr.min(), arr.max()
if arr_max - arr_min < 1e-6:
    arr_norm = np.zeros_like(arr, dtype=np.uint8)
else:
    arr_norm = ((arr - arr_min) / (arr_max - arr_min) * 255).astype(np.uint8)

# Create image and scale up
img = Image.fromarray(arr_norm, mode="L")
img = img.resize((WIDTH * SCALE, HEIGHT * SCALE), Image.NEAREST)

# Encode to base64 PNG
buf = io.BytesIO()
img.save(buf, format="PNG")
base64_str = base64.b64encode(buf.getvalue()).decode("utf-8")

# Print the base64 so PHP can read it
print(base64_str)
