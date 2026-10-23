#!/usr/bin/env python3
"""Stage 1 for Albania: split the 12 counties (albania_counties.png) into the 36 districts
(albania_districts.jpg) and write tools/_albania_inputs/partition.npz.
Seeds = the 36 red town dots on the district map; boundaries = faint pink dotted lines (watershed ridges)."""
import os, numpy as np
from PIL import Image
import scipy.ndimage as ndi
from skimage.segmentation import watershed

HERE = os.path.dirname(os.path.abspath(__file__)); IN = os.path.join(HERE, '_albania_inputs')
# name, district seat dot position on the 2x preview (x,y), terrain
DIST = [
 ('Malesi e Madhe','Koplik',(203,156),'mountain'), ('Tropoje','Bajram Curri',(388,122),'mountain'),
 ('Has','Kruma',(507,191),'mountain'), ('Shkoder','Shkoder',(227,239),'plains'),
 ('Puke','Puke',(341,244),'mountain'), ('Kukes','Kukes',(495,238),'mountain'),
 ('Lezhe','Lezhe',(265,352),'plains'), ('Mirdite','Rreshen',(334,357),'mountain'),
 ('Kurbin','Lac',(279,408),'hills'), ('Mat','Burrel',(369,420),'mountain'),
 ('Kruje','Kruje',(306,454),'hills'), ('Diber','Peshkopi',(495,387),'mountain'),
 ('Bulqize','Bulqize',(437,483),'mountain'), ('Durres','Durres',(205,530),'plains'),
 ('Tirane','Tirana',(316,530),'hills'), ('Kavaje','Kavaje',(237,590),'plains'),
 ('Librazhd','Librazhd',(469,581),'mountain'), ('Elbasan','Elbasan',(393,614),'hills'),
 ('Peqin','Peqin',(298,639),'plains'), ('Lushnje','Lushnje',(278,683),'plains'),
 ('Gramsh','Gramsh',(429,709),'hills'), ('Pogradec','Pogradec',(561,698),'mountain'),
 ('Kucove','Kucove',(343,739),'plains'), ('Fier','Fier',(239,772),'plains'),
 ('Berat','Berat',(353,780),'hills'), ('Mallakaster','Ballsh',(290,817),'hills'),
 ('Skrapar','Corovode',(436,855),'mountain'), ('Korce','Korce',(602,806),'hills'),
 ('Devoll','Bilisht',(661,802),'hills'), ('Vlore','Vlore',(222,874),'hills'),
 ('Tepelene','Tepelene',(371,933),'mountain'), ('Kolonje','Erseke',(567,909),'mountain'),
 ('Permet','Permet',(480,960),'mountain'), ('Gjirokaster','Gjirokaster',(414,1024),'mountain'),
 ('Delvine','Delvine',(380,1060),'hills'), ('Sarande','Sarande',(410,1146),'hills'),
]
assert len(DIST) == 36

def main():
    a = np.array(Image.open(os.path.join(IN, 'albania_districts.jpg')).convert('RGB')).astype(int)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    sea = (B > 200) & (R < 170) & (G > 170) & (G < 225) & (B - R > 60)
    sl, _ = ndi.label(sea)
    bd = set(sl[0, :]) | set(sl[-1, :]) | set(sl[:, 0]) | set(sl[:, -1]); bd.discard(0)
    land = ndi.binary_opening(ndi.binary_fill_holes(~np.isin(sl, list(bd))), iterations=1)
    dots = ndi.binary_dilation(ndi.binary_opening((R-G > 55) & (R-B > 45) & (R > 130), structure=np.ones((3, 3))), iterations=4)
    line = land & (R-G > 14) & (R-B > 10) & (G < 228) & ~dots
    line = ndi.binary_dilation(ndi.binary_closing(line, structure=np.ones((3, 3)), iterations=3), iterations=1)
    # the Delvine/Sarande boundary is not detected from the dotted line (the Sarande dot sits on it): draw it by hand
    from PIL import ImageDraw
    hand = Image.new('L', (land.shape[1], land.shape[0]), 0); dr = ImageDraw.Draw(hand)
    dr.line([(168, 544), (206, 544), (222, 541), (231, 560)], fill=255, width=2)
    line |= np.array(hand) > 0
    mk = np.zeros(land.shape, int)
    for i, (_, _, (x, y), _) in enumerate(DIST, 1):
        mk[y//2-2:y//2+3, x//2-2:x//2+3] = i
    lab1 = watershed(ndi.gaussian_filter(line.astype(float), 1.0), mk, mask=land)   # 1..36, 0 = sea (district map frame)
    # ---- register district frame -> county frame (bbox + small IoU refinement)
    cl = np.load(os.path.join(IN, 'county_labels.npy')) if os.path.exists(os.path.join(IN, 'county_labels.npy')) else None
    return lab1, land, cl

def bbox(m):
    ys, xs = np.where(m); return xs.min(), xs.max(), ys.min(), ys.max()

def warp(lab1, par, shape):
    sx, sy, tx, ty = par
    Y, X = np.mgrid[0:shape[0], 0:shape[1]]
    u = np.round((X - tx) / sx).astype(int); v = np.round((Y - ty) / sy).astype(int)
    ok = (u >= 0) & (u < lab1.shape[1]) & (v >= 0) & (v < lab1.shape[0])
    out = np.zeros(shape, int); out[ok] = lab1[v[ok], u[ok]]
    return out

def register(lab1, mask2):
    x0a, x1a, y0a, y1a = bbox(lab1 > 0); x0b, x1b, y0b, y1b = bbox(mask2)
    sx = (x1b - x0b) / (x1a - x0a); sy = (y1b - y0b) / (y1a - y0a)
    par = [sx, sy, x0b - x0a * sx, y0b - y0a * sy]
    def iou(p):
        w = warp(lab1, p, mask2.shape) > 0
        return (w & mask2).sum() / (w | mask2).sum()
    best = iou(par); step = [0.01, 0.01, 6, 6]
    for _ in range(6):
        for k in range(4):
            for d in (-1, 1):
                q = list(par); q[k] += d * step[k]
                v = iou(q)
                if v > best: best, par = v, q
        step = [t / 2 for t in step]
    return par, best

def combine(lab1, cl):
    mask2 = cl >= 0
    par, best = register(lab1, mask2)
    print('registration IoU %.3f scale %.3f/%.3f' % (best, par[0], par[1]))
    w = warp(lab1, par, mask2.shape); w[~mask2] = 0
    # county of each district = majority of its pixels
    dist_county = {}
    for d in range(1, 37):
        c = cl[(w == d)]; c = c[c >= 0]
        dist_county[d] = int(np.bincount(c, minlength=12).argmax()) if len(c) else -1
    P = np.zeros(mask2.shape, int) - 1
    for c in range(12):
        allowed = [d for d in range(1, 37) if dist_county[d] == c]
        inside = cl == c
        mk = np.where(inside & np.isin(w, allowed), w, 0)
        idx = ndi.distance_transform_edt(mk == 0, return_distances=False, return_indices=True)
        filled = mk[idx[0], idx[1]]
        P[inside] = filled[inside] - 1          # 0..35
    return P, dist_county

if __name__ == '__main__':
    lab1, land, cl = main()
    P, dc = combine(lab1, cl)
    names = ['Malësi e Madhe','Tropojë','Has','Shkodër','Pukë','Kukës','Lezhë','Mirditë','Kurbin','Mat','Krujë','Dibër','Bulqizë','Durrës','Tiranë','Kavajë','Librazhd','Elbasan','Peqin','Lushnjë','Gramsh','Pogradec','Kuçovë','Fier','Berat','Mallakastër','Skrapar','Korçë','Devoll','Vlorë','Tepelenë','Kolonjë','Përmet','Gjirokastër','Delvinë','Sarandë']
    cnt = {d: int((P == d - 1).sum()) for d in range(1, 37)}
    per_county = {}
    for d in range(1, 37): per_county.setdefault(dc[d], []).append(DIST[d-1][0])
    print({c: v for c, v in sorted(per_county.items())})
    print('smallest', sorted(cnt.items(), key=lambda kv: kv[1])[:5], 'empty', [DIST[d-1][0] for d, n in cnt.items() if n == 0])
    np.savez_compressed(os.path.join(IN, 'partition.npz'), P=P, county=cl, dist_county=np.array([dc[d] for d in range(1, 37)]))
