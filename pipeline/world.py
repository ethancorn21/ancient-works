"""Reproject NASA Blue Marble (equirectangular) to a square Web Mercator texture for the globe base."""
import sys
import numpy as np
from PIL import Image

src = np.asarray(Image.open(sys.argv[1]).convert("RGB"))
size = int(sys.argv[3]) if len(sys.argv) > 3 else 4096
h_src = src.shape[0]
y = (np.arange(size) + 0.5) / size
lat = np.degrees(np.arctan(np.sinh(np.pi * (1 - 2 * y))))
rows = np.clip(((90 - lat) / 180 * h_src).astype(int), 0, h_src - 1)
merc = src[rows]
out = Image.fromarray(merc).resize((size, size), Image.LANCZOS)
out.save(sys.argv[2], quality=86, optimize=True)
print("wrote", sys.argv[2], out.size)
