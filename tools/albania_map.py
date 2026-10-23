#!/usr/bin/env python3
"""Stage 2 for Albania. Run AFTER tools/albania_partition.py. Re-runnable ONLY on a map that does not yet contain Albania
(it reads map/*.bmp and map/definition.csv in place; keep a backup of the original map before running).
- places the 36 district provinces on the 2048x2048 map (scale 0.35, snapped to Montenegro/Kosovo/Macedonia, clipped by them)
- cleans fragments, writes map/provinces.bmp, map/heightmap.bmp, map/world_normal.bmp
- appends 36 land provinces (ids 1246..1281) to map/definition.csv, refreshes the coastal flag of every land province
- writes tools/_albania_inputs/provinces_meta.json for the later stages"""
import os, csv, json, sys, numpy as np
from PIL import Image
import scipy.ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); IN = os.path.join(HERE, '_albania_inputs')
sys.path.insert(0, HERE)
from albania_partition import DIST

S, X0, Y0 = 0.35, 1190, 1310
COUNTY = ['Korçë', 'Shkodër', 'Elbasan', 'Gjirokastër', 'Vlorë', 'Dibër', 'Kukës', 'Fier', 'Berat', 'Tiranë', 'Lezhë', 'Durrës']
NAMES = ['Malësi e Madhe', 'Tropojë', 'Has', 'Shkodër', 'Pukë', 'Kukës', 'Lezhë', 'Mirditë', 'Kurbin', 'Mat', 'Krujë', 'Dibër',
         'Bulqizë', 'Durrës', 'Tiranë', 'Kavajë', 'Librazhd', 'Elbasan', 'Peqin', 'Lushnjë', 'Gramsh', 'Pogradec', 'Kuçovë', 'Fier',
         'Berat', 'Mallakastër', 'Skrapar', 'Korçë', 'Devoll', 'Vlorë', 'Tepelenë', 'Kolonjë', 'Përmet', 'Gjirokastër', 'Delvinë', 'Sarandë']
FIRST_ID = 1246


def rd(p, mode=None):
    im = Image.open(os.path.join(ROOT, p)); return np.array(im.convert(mode) if mode else im)


def place(P):
    """P: province ids 0..35 (-1 outside) in the 960x2087 county-map frame -> map frame (2048x2048, -1 outside)."""
    land = np.load(os.path.join(HERE, '_albania_inputs', 'land_mask.npy'))
    h, w = int(P.shape[0] * S), int(P.shape[1] * S)
    A = np.array(Image.fromarray((P + 1).astype(np.uint8)).resize((w, h), Image.NEAREST)).astype(int) - 1
    full = np.full((2048, 2048), -1, int); full[Y0:Y0 + h, X0:X0 + w] = A
    out = np.full((2048, 2048), -1, int)
    MAXG = 90
    tl = np.zeros(2048); tr = np.zeros(2048); xmn = np.zeros(2048, int); xmx = np.zeros(2048, int); has = np.zeros(2048, bool)
    for y in range(Y0, Y0 + h):
        xs = np.where(full[y] >= 0)[0]
        if len(xs) == 0: continue
        a, b = xs.min(), xs.max(); has[y] = True; xmn[y], xmx[y] = a, b
        seg = land[y, max(0, a - MAXG):a]
        if seg.any(): tl[y] = len(seg) - 1 - np.where(seg)[0].max()
        seg = land[y, b + 1:b + 1 + MAXG]
        if seg.any(): tr[y] = np.where(seg)[0].min()
    tls = ndi.gaussian_filter1d(tl, 6); trs = ndi.gaussian_filter1d(tr, 6)
    for y in range(Y0, Y0 + h):
        if not has[y]: continue
        a, b = xmn[y], xmx[y]
        na, nb = int(round(a - tls[y])), int(round(b + trs[y]))
        xsr = np.arange(na, nb + 1)
        src = (a + (xsr - na) * (b - a) / max(1, nb - na)).round().astype(int)
        out[y, xsr] = full[y, src]
    out[land] = -1
    return out


def components_fix(key, only, alb_keys):
    """Merge fragments: every province must be a single connected area. Fragments go to the neighbour sharing the longest border
    (Albanian provinces preferred)."""
    changed = 0
    for it in range(3):
        for c in only:
            m = key == c
            lab, n = ndi.label(m)
            if n <= 1: continue
            sizes = ndi.sum(m, lab, range(1, n + 1)); keep = int(np.argmax(sizes)) + 1
            for k in range(1, n + 1):
                if k == keep: continue
                frag = lab == k
                ring = ndi.binary_dilation(frag, iterations=1) & ~frag
                nb = key[ring]; nb = nb[nb != c]
                if len(nb) == 0: continue
                vals, cnt = np.unique(nb, return_counts=True)
                prefer = [(cn, v) for v, cn in zip(vals, cnt) if v in alb_keys]
                tgt = max(prefer)[1] if prefer else vals[cnt.argmax()]
                key[frag] = tgt; changed += 1
    return changed


def main():
    z = np.load(os.path.join(IN, 'partition.npz')); P = z['P']; dist_county = z['dist_county']
    prov = rd('map/provinces.bmp', 'RGB')
    key = (prov[..., 0].astype(np.int64) << 16) | (prov[..., 1].astype(np.int64) << 8) | prov[..., 2]
    rows = [r for r in csv.reader(open(os.path.join(ROOT, 'map/definition.csv'), encoding='utf-8'), delimiter=';')]
    hdr = rows[0] if not rows[0][0].isdigit() else None
    body = [r for r in rows if len(r) >= 8 and r[0].isdigit()]
    ids = [int(r[0]) for r in body]
    assert ids == list(range(len(ids))), 'definition.csv ids must be sequential'
    if len(body) > FIRST_ID:
        sys.exit('definition.csv already has %d provinces - Albania seems to be inserted already (restore the original map first)' % len(body))
    assert len(body) == FIRST_ID, len(body)
    ckeys = {(int(r[1]) << 16) | (int(r[2]) << 8) | int(r[3]): r for r in body}
    typ = {k: r[4] for k, r in ckeys.items()}
    land = np.isin(key, [k for k, t in typ.items() if t == 'land' and k != 0])
    np.save(os.path.join(IN, 'land_mask.npy'), land)

    PM = place(P)
    # colours for new provinces: unique, away from existing ones
    used = set(ckeys); rng = np.random.RandomState(1990); newcol = []
    while len(newcol) < 36:
        c = (int(rng.randint(40, 250)) << 16) | (int(rng.randint(40, 250)) << 8) | int(rng.randint(40, 250))
        if c not in used: used.add(c); newcol.append(c)
    newkeys = np.array(newcol)
    alb = PM >= 0
    key2 = key.copy(); key2[alb] = newkeys[PM[alb]]
    pre = [int((PM == i).sum()) for i in range(36)]
    print('areas before cleanup', pre)
    touched = set(int(v) for v in np.unique(key[alb]))      # sea provinces that lost pixels to Albania
    n_fix = components_fix(key2, list(touched) + newcol, set(newcol))
    print('fragments merged:', n_fix)
    PM2 = np.full(key2.shape, -1, int)
    for i, c in enumerate(newcol): PM2[key2 == c] = i
    # every province must still be one piece and big enough
    area = [(int((PM2 == i).sum())) for i in range(36)]
    dead = [i for i in range(36) if area[i] < 300]
    print('dropped (clipped away by neighbours):', [NAMES[i] for i in dead])
    for i in dead:                      # leftover pixels (if any) go to the neighbour with the longest border
        frag = key2 == newcol[i]
        if frag.any():
            ring = ndi.binary_dilation(frag) & ~frag; nb = key2[ring]; v, c = np.unique(nb, return_counts=True)
            key2[frag] = v[c.argmax()]
    alive = [i for i in range(36) if i not in dead]
    present = set(int(v) for v in np.unique(key2))
    vanished = sorted(int(r[0]) for r in body if r[4] == 'sea' and ((int(r[1]) << 16) | (int(r[2]) << 8) | int(r[3])) not in present)
    idpool = (vanished + [FIRST_ID + k for k in range(len(alive))])[:len(alive)]
    print('sea provinces fully covered by Albania (their ids are reused):', len(vanished))
    print('province areas min/max', min(area[i] for i in alive), max(area[i] for i in alive), 'count', len(alive))

    # ---- write provinces.bmp
    out = np.stack([(key2 >> 16) & 255, (key2 >> 8) & 255, key2 & 255], -1).astype(np.uint8)
    Image.fromarray(out).save(os.path.join(ROOT, 'map/provinces.bmp'), format='BMP')

    # ---- coastal flag for every land province (adjacent to a sea province pixel)
    sea_keys = [k for k, t in typ.items() if t == 'sea']
    sea_mask = np.isin(key2, sea_keys)
    sea_edge = ndi.binary_dilation(sea_mask, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
    flag_changes = 0; new_rows = []
    for r in body:
        r = list(r)
        if r[4] == 'land' and int(r[0]) != 0:
            k = (int(r[1]) << 16) | (int(r[2]) << 8) | int(r[3])
            m = key2 == k
            coastal = bool((m & sea_edge).any())
            val = 'true' if coastal else 'false'
            if val != r[5]: flag_changes += 1; r[5] = val
        new_rows.append(r)
    meta = []
    sea_edge4 = sea_edge
    for j, i in enumerate(alive):
        m = PM2 == i; ys, xs = np.where(m)
        coastal = bool((m & sea_edge4).any())
        cx, cy = float(xs.mean()), float(ys.mean())
        terr = DIST[i][3]
        nid = idpool[j]; c = newcol[i]
        row = [str(nid), str((c >> 16) & 255), str((c >> 8) & 255), str(c & 255), 'land', 'true' if coastal else 'false', terr, '1']
        if nid < FIRST_ID: new_rows[nid] = row
        else: new_rows.append(row)
        meta.append(dict(id=nid, name=NAMES[i], ascii=DIST[i][0], seat=DIST[i][1], county=COUNTY[int(dist_county[i])], terrain=terr,
                         coastal=coastal, cx=cx, cy=cy, area=int(m.sum()), rgb=[(c >> 16) & 255, (c >> 8) & 255, c & 255]))
    print('coastal flags changed on existing land provinces:', flag_changes)
    with open(os.path.join(ROOT, 'map/definition.csv'), 'w', encoding='utf-8', newline='') as f:
        if hdr: f.write(';'.join(hdr) + '\n')
        for r in new_rows: f.write(';'.join(r) + '\n')

    # ---- heightmap (land 96..255, sea 0)
    h = rd('map/heightmap.bmp').astype(float)
    base = np.zeros(h.shape); noise = ndi.gaussian_filter(np.random.RandomState(7).randn(*h.shape), 5)
    noise = noise / noise.std()
    bh = {'plains': 100, 'hills': 128, 'mountain': 175}
    for i in alive: base[PM2 == i] = bh[DIST[i][3]]
    msk = PM2 >= 0
    # smooth the per-province base inside Albania (normalised convolution)
    num = ndi.gaussian_filter(np.where(msk, base, 0.0), 14); den = ndi.gaussian_filter(msk.astype(float), 14)
    sm = np.where(msk, num / np.maximum(den, 1e-6), 0)
    amp = np.where(sm > 140, 28, np.where(sm > 112, 14, 4))
    alt = np.clip(sm + noise * amp, 96, 255)
    # feather into the neighbours' existing heights along the shared border
    d_to_old = ndi.distance_transform_edt(~land)       # distance from existing land
    w = np.clip(d_to_old / 22.0, 0, 1)
    nbh = ndi.gaussian_filter(np.where(land, h, 0.0), 10) / np.maximum(ndi.gaussian_filter(land.astype(float), 10), 1e-6)
    alt = np.where(msk, w * alt + (1 - w) * np.clip(nbh, 96, 255), h)
    # coast: ease towards sea level
    d_to_sea = ndi.distance_transform_edt(msk)          # distance to the edge of Albania (sea or neighbours)
    ctl = np.clip(d_to_sea / 18.0, 0, 1)
    alt = np.where(msk, np.clip(96 + (alt - 96) * np.maximum(ctl, 0.25), 96, 255), alt)
    h2 = h.copy(); h2[msk] = np.round(alt[msk])
    Image.fromarray(h2.astype(np.uint8), 'L').save(os.path.join(ROOT, 'map/heightmap.bmp'), format='BMP')

    # ---- world_normal: derive from heightmap, convention fitted on existing land
    nm = rd('map/world_normal.bmp', 'RGB').astype(float)
    gy, gx = np.gradient(ndi.gaussian_filter(h, 1.2)); mm = land
    def fit(ch, g):
        a = (nm[..., ch][mm] - 127.5); b = g[mm]
        k = (a * b).sum() / (b * b).sum(); r = np.corrcoef(a, b)[0, 1]
        return k, r
    kx, rx = fit(0, gx); ky, ry = fit(1, gy)
    print('normal fit  R~gx k=%.2f r=%.2f   G~gy k=%.2f r=%.2f' % (kx, rx, ky, ry))
    gy2, gx2 = np.gradient(ndi.gaussian_filter(h2, 1.2))
    band = ndi.binary_dilation(msk, iterations=3)
    nm2 = nm.copy()
    nm2[..., 0][band] = np.clip(127.5 + kx * gx2[band], 0, 255)
    nm2[..., 1][band] = np.clip(127.5 + ky * gy2[band], 0, 255)
    nx = (nm2[..., 0][band] - 127.5) / 127.5; ny = (nm2[..., 1][band] - 127.5) / 127.5
    nm2[..., 2][band] = np.clip(127.5 + 127.5 * np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1)), 0, 255)
    Image.fromarray(nm2.astype(np.uint8), 'RGB').save(os.path.join(ROOT, 'map/world_normal.bmp'), format='BMP')

    json.dump(dict(provinces=meta, reused_sea_ids=vanished, first_new_id=FIRST_ID), open(os.path.join(IN, 'provinces_meta.json'), 'w'), ensure_ascii=False, indent=1)
    rast = np.full(PM2.shape, -1, np.int16)
    for j, i in enumerate(alive): rast[PM2 == i] = j
    np.save(os.path.join(IN, 'province_raster.npy'), rast)   # 0..len(alive)-1 = meta order
    print('done: %d provinces, ids reused %d, new ids %d..%d' % (len(alive), len(vanished), FIRST_ID, max(idpool)))


if __name__ == '__main__':
    main()
