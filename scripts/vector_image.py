#!/usr/bin/env python3
import sys
import os
import numpy as np
from PIL import Image

if len(sys.argv) != 3:
    print("Usage: python3 vector_image.py <embedding_csv> <word>")
    sys.exit(1)

embedding_csv = sys.argv[1]
word = sys.argv[2]

embedding = np.array([float(x) for x in embedding_csv.split(',')], dtype=float)

# Reshape, scale, etc.
WIDTH, HEIGHT = 15, 20
SCALE = 20

arr = embedding.reshape((HEIGHT, WIDTH))

# Normalize
arr_min, arr_max = arr.min(), arr.max()
if arr_max - arr_min < 1e-6:
    arr_norm = np.zeros_like(arr, dtype=np.uint8)
else:
    arr_norm = ((arr - arr_min) / (arr_max - arr_min) * 255).astype(np.uint8)

img = Image.fromarray(arr_norm, mode="L")
img = img.resize((WIDTH*SCALE, HEIGHT*SCALE), Image.NEAREST)

IMG_DIR = "/var/www/wordchef.app/html/imgs"
os.makedirs(IMG_DIR, exist_ok=True)
img_path = os.path.join(IMG_DIR, f"{word}.png")
img.save(img_path)

print(img_path)