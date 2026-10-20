#!/usr/bin/env python3
"""Analyze provinces geography and map key cities for state redesign."""
import sys, re, glob, csv, json
sys.stdout.reconfigure(encoding='utf-8')

# 1. Read all province positions
prov_pos = {}
with open('map/positions.txt', 'r', encoding='utf-8') as f:
    for line in f:
        p = line.strip().split(';')
        if len(p) >= 4 and p[0].isdigit():
            pid = int(p[0])
            if 1 <= pid <= 507:
                prov_pos[pid] = (float(p[1]), float(p[3]))

# 2. Read definition.csv for terrain/coastal
prov_terrain = {}
with open('map/definition.csv', 'r', encoding='utf-8') as f:
    for line in f:
        p = line.strip().split(';')
        if len(p) >= 8 and p[0].isdigit():
            pid = int(p[0])
            if 1 <= pid <= 507:
                coastal = p[5] == 'true'
                terrain = p[6]
                prov_terrain[pid] = (coastal, terrain)

# 3. Read current states
state_provs = {}
for file in sorted(glob.glob('history/states/*.txt')):
    with open(file, 'r', encoding='utf-8') as f:
        c = f.read()
    sid = int(re.search(r'id\s*=\s*(\d+)', c).group(1))
    p_match = re.search(r'provinces\s*=\s*\{([^}]+)\}', c)
    provs = [int(x) for x in p_match.group(1).split() if x.isdigit()]
    mp = int(re.search(r'manpower\s*=\s*(\d+)', c).group(1))
    state_provs[sid] = {'provs': provs, 'manpower': mp}

# 4. Read state_names.csv
vp_map = {}
with open('tools/state_names.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f, delimiter=';')
    next(reader)
    for r in reader:
        sid = int(r[0])
        vp_prov = int(r[1])
        name_en = r[3]
        vp_city = r[5]
        vp_map[sid] = {'vp_prov': vp_prov, 'name': name_en, 'city': vp_city}

# 5. Map bounds
xs = [prov_pos[p][0] for p in prov_pos]
zs = [prov_pos[p][1] for p in prov_pos]
print(f'=== Map bounds ===')
print(f'X: {min(xs):.0f} .. {max(xs):.0f}')
print(f'Z: {min(zs):.0f} .. {max(zs):.0f}')

# 6. Find ALL VP provinces with their coordinates
print()
print('=== All VP cities with coordinates (sorted by name) ===')
entries = []
for sid, info in sorted(vp_map.items()):
    vp = info['vp_prov']
    if vp in prov_pos:
        x, z = prov_pos[vp]
        entries.append((sid, info['city'], info['name'], vp, x, z))

for sid, city, name, vp, x, z in sorted(entries, key=lambda e: e[1]):
    print(f'  St={sid:3d}  vp_prov={vp:3d}  city={city:25s}  region={name:30s}  X={x:7.1f}  Z={z:7.1f}')

# 7. Dump all provinces with coords to JSON for analysis
prov_list = []
for pid in sorted(prov_pos.keys()):
    x, z = prov_pos[pid]
    coastal, terrain = prov_terrain.get(pid, (False, 'unknown'))
    prov_list.append({
        'id': pid, 'x': round(x, 1), 'z': round(z, 1),
        'coastal': coastal, 'terrain': terrain
    })

with open('tools/province_coords.json', 'w', encoding='utf-8') as f:
    json.dump(prov_list, f, indent=1)
print(f'\nWrote tools/province_coords.json ({len(prov_list)} provinces)')

# 8. Current state sizes
print()
print('=== Current state size distribution ===')
sizes = {}
for sid, data in state_provs.items():
    sz = len(data['provs'])
    sizes.setdefault(sz, []).append(sid)
for sz in sorted(sizes.keys()):
    print(f'  {sz} provinces: {len(sizes[sz])} states  ({sorted(sizes[sz])})')
