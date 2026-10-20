#!/usr/bin/env python3
"""
YGwar State Redesign — assign 507 land provinces to ~100 states
based on historical Yugoslav republican borders (AVNOJ) and
1991-1995 conflict zones.

Strategy:
1. Define "seed" provinces for each republic from known VP cities.
2. Use Voronoi-like assignment: each province goes to the nearest
   seed weighted by republic affinity.
3. Then cluster within each republic into 5-20 states of 3-8 provinces.
4. Output: tools/new_states.json  (province->state mapping)

Run:  python tools/build_states.py
"""
import sys, json, math, re, glob, csv, os
sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# ── 1. Load province positions ──────────────────────────────────
prov_pos = {}
with open('map/positions.txt', 'r', encoding='utf-8') as f:
    for line in f:
        p = line.strip().split(';')
        if len(p) >= 4 and p[0].isdigit():
            pid = int(p[0])
            if 1 <= pid <= 507:
                prov_pos[pid] = (float(p[1]), float(p[3]))

prov_coastal = {}
with open('map/definition.csv', 'r', encoding='utf-8') as f:
    for line in f:
        p = line.strip().split(';')
        if len(p) >= 8 and p[0].isdigit():
            pid = int(p[0])
            if 1 <= pid <= 507:
                prov_coastal[pid] = (p[5] == 'true')

# ── 2. Load current states (to preserve province lists) ────────
cur_states = {}
for file in sorted(glob.glob('history/states/*.txt')):
    with open(file, 'r', encoding='utf-8') as f:
        c = f.read()
    sid = int(re.search(r'id\s*=\s*(\d+)', c).group(1))
    p_match = re.search(r'provinces\s*=\s*\{([^}]+)\}', c)
    provs = [int(x) for x in p_match.group(1).split() if x.isdigit()]
    mp = int(re.search(r'manpower\s*=\s*(\d+)', c).group(1))
    cur_states[sid] = {'provs': provs, 'manpower': mp}

# ── 3. Load state_names.csv for VP cities ───────────────────────
vp_cities = {}
with open('tools/state_names.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f, delimiter=';')
    next(reader)
    for r in reader:
        sid = int(r[0])
        vp_prov = int(r[1])
        vp_cities[sid] = {
            'vp_prov': vp_prov,
            'name_en': r[3],
            'city_en': r[5],
        }

# ── 4. Define republican seeds ──────────────────────────────────
# Each republic is defined by known city coordinates.
# We assign every province to the nearest republic.

# Republic boundary seeds (prov_id, republic_tag)
# Derived from VP cities and known geography:
REPUBLIC_SEEDS = {
    # SLOVENIA: northwest corner, X ~150-600, Z ~1400-1790
    'SVN': [63, 69, 10, 61, 29, 60, 23, 96, 93, 1],  # Ljubljana, Maribor, Tolmin, NovaGorica, Sezana, NovoMesto, Mozirje, SlovenjGradec, Krsko, MurskaSobota

    # CROATIA: west/northwest band
    'CRO': [95, 35, 72, 20, 90, 31, 6, 48, 58, 43, 36, 59, 91, 5, 56, 74, 85, 78, 81, 47, 3],
    # Zagreb, Krapina, Cakovec, Bjelovar, Virovitica, Osijek, SlBrod, Pozega, NovaGradiska, Sisak, GorskiKotar, Buje, Pazin, Pula, Zadar, Otocac, Sibenik, Makarska, Dubrovnik, Sinj, Peljesac

    # RSK KRAJINA: Serb-held areas in Croatia (1991-1995)
    'RSK': [8, 24, 39, 14, 87, 62, 22, 49],
    # Knin, Gospic/Lika, Korenica, Slunj/Kordun, Dvor/Banija, Drvar, SanskiMost, Vinkovci/Srijem

    # BOSNIA - Bosniak
    'BOS': [21, 84, 34, 52],
    # Travnik, Zenica/Vares, Tuzla, Konjic

    # REPUBLIKA SRPSKA
    'RSB': [50, 73, 12, 32],
    # BanjaLuka, Teslic, Sokolac/Romanija, Foca

    # HERCEG-BOSNA (Croat areas in Bosnia)
    'HRZ': [46, 89],
    # Mostar, Glamoc

    # SERBIA proper
    'SER': [55, 18, 66, 92, 41, 17, 94, 51, 33, 86, 80, 44, 26, 45, 53, 65, 16],
    # NoviSad area, SremskaMitrovica, Sabac, Ub, Valjevo, Kragujevac, Cacak, Kraljevo, Ivanjica, Krusevac, Smederevo, Petrovac, Nis, Leskovac, Zajecar, Knjazevac, Negotin

    # VOJVODINA
    'VOJ': [11, 30, 71, 88, 40, 68, 4, 55],
    # Subotica, Kikinda, Becej, Zrenjanin, Pancevo, Alibunar, Vrsac, JuznaBacka

    # KOSOVO
    'KOS': [54, 83, 79, 28],
    # Pristina, Podujevo, Djakovica, Prizren

    # MONTENEGRO
    'MNT': [70, 38, 15, 25, 57, 76],
    # Niksic, HercegNovi, Bar, BijeloPolje, Berane, Pljevlja

    # MACEDONIA
    'MAC': [82, 19, 42, 13, 67, 2, 37, 77, 97],
    # Skopje, Kumanovo, Bitola, Ohrid, Stip, Strumica, Berovo, Gostivar, KrivaPalanka
}

# Build republic centroids from VP province positions
republic_centers = {}
for rep, state_ids in REPUBLIC_SEEDS.items():
    pts = []
    for sid in state_ids:
        if sid in vp_cities:
            vp = vp_cities[sid]['vp_prov']
            if vp in prov_pos:
                pts.append(prov_pos[vp])
    if pts:
        cx = sum(p[0] for p in pts) / len(pts)
        cz = sum(p[1] for p in pts) / len(pts)
        republic_centers[rep] = (cx, cz)
        print(f'{rep}: center=({cx:.0f}, {cz:.0f}) from {len(pts)} seed cities')

# ── 5. Assign each province to nearest republic ─────────────────
def dist(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

# But simple Voronoi won't work well for interleaved zones like RSK/CRO.
# We need to use the VP provinces as hard anchors:
# each province in an existing state inherits its VP's republic.

# Build: state_id -> republic assignment from seeds
state_republic = {}
for rep, state_ids in REPUBLIC_SEEDS.items():
    for sid in state_ids:
        if sid not in state_republic:
            state_republic[sid] = rep

# Assign unassigned states to nearest republic center
for sid in cur_states:
    if sid not in state_republic:
        provs = cur_states[sid]['provs']
        # centroid of state
        pts = [prov_pos[p] for p in provs if p in prov_pos]
        if not pts:
            continue
        cx = sum(p[0] for p in pts) / len(pts)
        cz = sum(p[1] for p in pts) / len(pts)
        best_rep = min(republic_centers, key=lambda r: dist((cx, cz), republic_centers[r]))
        state_republic[sid] = best_rep

# ── 6. Report assignment ────────────────────────────────────────
print('\n=== Republic assignments (current states -> republics) ===')
rep_states = {}
for sid, rep in sorted(state_republic.items()):
    rep_states.setdefault(rep, []).append(sid)

total_provs = 0
total_mp = 0
for rep in ['SVN', 'CRO', 'RSK', 'BOS', 'RSB', 'HRZ', 'SER', 'VOJ', 'KOS', 'MNT', 'MAC']:
    states = sorted(rep_states.get(rep, []))
    n_provs = sum(len(cur_states[s]['provs']) for s in states)
    n_mp = sum(cur_states[s]['manpower'] for s in states)
    total_provs += n_provs
    total_mp += n_mp
    city_names = []
    for s in states:
        if s in vp_cities:
            city_names.append(vp_cities[s]['city_en'])
    print(f'\n  {rep} ({len(states)} states, {n_provs} provs, pop={n_mp:,}):')
    print(f'    States: {states}')
    print(f'    Cities: {", ".join(city_names)}')

print(f'\nTOTAL: {total_provs} provs, {total_mp:,} manpower')

# ── 7. Save result ──────────────────────────────────────────────
result = {
    'republic_assignments': {str(sid): rep for sid, rep in state_republic.items()},
    'republic_states': {rep: sorted(sids) for rep, sids in rep_states.items()},
}
with open('tools/republic_assignments.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print('\nWrote tools/republic_assignments.json')
