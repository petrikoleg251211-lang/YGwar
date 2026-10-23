#!/usr/bin/env python3
"""Renders the political overview of the whole YGwar map -> YGwar_full_map.png (run from the mod root or tools/)."""
import re, glob, csv, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from skimage.segmentation import find_boundaries
import scipy.ndimage as ndi
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'YGwar_full_map.png')
os.chdir(ROOT)
rows = [r for r in csv.reader(open('map/definition.csv'), delimiter=';') if len(r) >= 8]
col2id = {((int(r[1]) << 16) | (int(r[2]) << 8) | int(r[3])): int(r[0]) for r in rows}
typ = {int(r[0]): r[4] for r in rows}
a = np.array(Image.open('map/provinces.bmp').convert('RGB'))
key = (a[..., 0].astype(np.int64) << 16) | (a[..., 1].astype(np.int64) << 8) | a[..., 2]
lk = np.array(sorted(col2id)); li = np.array([col2id[k] for k in lk]); pid = li[np.searchsorted(lk, key)]
PRIM = ['SVN', 'CRO', 'BOS', 'SER', 'MNT', 'MAC', 'VOJ', 'KOS', 'ALB']
prov2state = {}; state_tag = {}
for f in glob.glob('history/states/*.txt'):
    t = open(f, encoding='utf-8').read(); sid = int(re.search(r'\bid\s*=\s*(\d+)', t).group(1))
    cores = re.findall(r'add_core_of\s*=\s*(\w+)', t)
    state_tag[sid] = next((c for c in cores if c in PRIM), next((c for c in cores if c != 'YUG'), 'YUG'))
    for p in re.search(r'provinces\s*=\s*\{([^}]*)\}', t).group(1).split(): prov2state[int(p)] = sid
maxp = int(max(pid.max(), max(prov2state) if prov2state else 0)) + 1
stlut = np.zeros(maxp + 1, int)
for p, s in prov2state.items(): stlut[p] = s
st = stlut[pid]; landm = np.isin(pid, [p for p, t in typ.items() if t == 'land'])
COL = {'SVN': (120, 190, 120), 'CRO': (225, 120, 120), 'BOS': (235, 205, 110), 'SER': (120, 150, 215), 'MNT': (170, 120, 200),
       'MAC': (235, 160, 90), 'VOJ': (110, 200, 200), 'KOS': (205, 140, 170), 'ALB': (190, 60, 90)}
NAME = {'SVN': 'SLOVENIA', 'CRO': 'CROATIA', 'BOS': 'BOSNIA &\nHERZEGOVINA', 'SER': 'SERBIA', 'MNT': 'MONTENEGRO', 'MAC': 'MACEDONIA',
        'VOJ': 'VOJVODINA', 'KOS': 'KOSOVO', 'ALB': 'ALBANIA'}
img = np.zeros(key.shape + (3,), np.uint8); img[:] = (168, 203, 232)
idx = {t: i + 1 for i, t in enumerate(PRIM)}; cty = np.zeros(st.shape, int)
for s, t in state_tag.items():
    m = (st == s) & landm; img[m] = COL[t]; cty[m] = idx[t]
pb = find_boundaries(pid) & landm; img[pb] = (img[pb] * 0.8).astype(np.uint8)
img[find_boundaries(st * landm, mode='inner') & landm] = (60, 60, 60)
img[ndi.binary_dilation(find_boundaries(cty, mode='inner') & (cty > 0), iterations=1) & (cty > 0)] = (20, 20, 20)
ys, xs = np.where(landm)
x0, x1, y0, y1 = max(0, xs.min() - 30), min(2048, xs.max() + 30), max(0, ys.min() - 30), min(2048, ys.max() + 30)
im = Image.fromarray(img); d = ImageDraw.Draw(im)
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
fb = ImageFont.truetype(FB, 22); fs = ImageFont.truetype(FR, 10)
for s in sorted(state_tag):
    m = (st == s) & landm
    if m.any():
        yy, xx = np.where(m); d.text((xx.mean() - 6, yy.mean() - 5), str(s), fill=(40, 40, 40), font=fs)
for t in PRIM:
    m = cty == idx[t]; dist = ndi.distance_transform_edt(m); cy, cx = np.unravel_index(dist.argmax(), dist.shape)
    bb = d.multiline_textbbox((0, 0), NAME[t], font=fb, align='center'); wd, ht = bb[2] - bb[0], bb[3] - bb[1]
    d.multiline_text((cx - wd / 2 + 1, cy - ht / 2 + 1), NAME[t], fill=(255, 255, 255), font=fb, align='center')
    d.multiline_text((cx - wd / 2, cy - ht / 2), NAME[t], fill=(0, 0, 0), font=fb, align='center')
im = im.crop((x0, y0, x1, y1)); d = ImageDraw.Draw(im)
d.text((14, 10), 'YGwar - full map, 1990   (colour = main republic of the state; numbers = state ids; Albania = states 121-132)', fill=(0, 0, 0), font=ImageFont.truetype(FR, 16))
im.save(OUT); print(im.size, '->', OUT)
