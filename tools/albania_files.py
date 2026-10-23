#!/usr/bin/env python3
"""Stage 3 for Albania. Run AFTER tools/albania_map.py (needs tools/_albania_inputs/provinces_meta.json + province_raster.npy).
Single-shot like stage 2: restore the original map/ and history/ first if you want to re-run.
Creates: history/states/121..132, history/countries/ALB, history/units/ALB_OOB, map/strategicregions/3_albania.txt,
rows in map/positions.txt, unitstacks.txt, buildings.txt, supply_nodes.txt, railways.txt, airports.txt, tag registration (tags, colors,
AI, unit names, MIO lists, leader) and localisation (en/ru)."""
import os, re, json, collections, numpy as np
from PIL import Image
import scipy.ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); IN = os.path.join(HERE, '_albania_inputs')
meta_all = json.load(open(os.path.join(IN, 'provinces_meta.json'), encoding='utf-8'))
PROV = meta_all['provinces']; REUSED = set(meta_all['reused_sea_ids'])
RAST = np.load(os.path.join(IN, 'province_raster.npy'))             # -1 outside, else index into PROV
rng = np.random.RandomState(1992)

# county -> (state id, en, ru, 1990 population, main province ascii name, victory points value, VP en, VP ru, resources)
COUNTIES = [
 ('Shkodër',     121, 'Shkodër',     'Шкодер',      230000, 'Shkoder',     3, 'Shkodër',     'Шкодер',      {}),
 ('Kukës',       122, 'Kukës',       'Кукес',       105000, 'Kukes',       2, 'Kukës',       'Кукес',       {'chromium': 6}),
 ('Lezhë',       123, 'Lezhë',       'Леже',        135000, 'Lezhe',       2, 'Lezhë',       'Леже',        {}),
 ('Dibër',       124, 'Dibër',       'Дибер',       135000, 'Diber',       2, 'Peshkopi',    'Пешкопи',     {'chromium': 12}),
 ('Durrës',      125, 'Durrës',      'Дуррес',      245000, 'Durres',      6, 'Durrës',      'Дуррес',      {}),
 ('Tiranë',      126, 'Tiranë',      'Тирана',      450000, 'Tirane',      15, 'Tiranë',      'Тирана',      {}),
 ('Elbasan',     127, 'Elbasan',     'Эльбасан',    330000, 'Elbasan',     5, 'Elbasan',     'Эльбасан',    {'steel': 4}),
 ('Fier',        128, 'Fier',        'Фиер',        340000, 'Fier',        4, 'Fier',        'Фиер',        {'oil': 4}),
 ('Berat',       129, 'Berat',       'Берат',       190000, 'Berat',       3, 'Berat',       'Берат',       {}),
 ('Korçë',       130, 'Korçë',       'Корча',       270000, 'Korce',       4, 'Korçë',       'Корча',       {}),
 ('Gjirokastër', 131, 'Gjirokastër', 'Гирокастра',  120000, 'Gjirokaster', 3, 'Gjirokastër', 'Гирокастра',  {}),
 ('Vlorë',       132, 'Vlorë',       'Влёра',       200000, 'Vlore',       4, 'Vlorë',       'Влёра',       {}),
]
CAPITAL_STATE = 126


def w(rel, text, mode='w'):
    p = os.path.join(ROOT, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, mode, encoding='utf-8', newline='\n') as f: f.write(text)


def rd(rel):
    return open(os.path.join(ROOT, rel), encoding='utf-8', errors='ignore').read()


def pole(mask):
    d = ndi.distance_transform_edt(mask); y, x = np.unravel_index(d.argmax(), d.shape); return x, y


def main():
    # ------------------------------------------------------------ manpower scale + categories from the existing states
    mp = []
    for fn in os.listdir(os.path.join(ROOT, 'history/states')):
        t = rd('history/states/' + fn); m = re.search(r'manpower\s*=\s*(\d+)', t)
        if m: mp.append(int(m.group(1)))
    ratio = sum(mp) / 23_500_000.0
    print('manpower / population ratio in the mod: %.3f' % ratio)

    # ------------------------------------------------------------ states
    by_county = collections.defaultdict(list)
    for m in PROV: by_county[m['county']].append(m)
    vp_loc = {}; state_of_prov = {}
    for cname, sid, en, ru, pop, main_prov, vpv, vpen, vpru, res in COUNTIES:
        provs = sorted(by_county[cname], key=lambda m: m['id'])
        assert provs, cname
        mainp = next((m for m in provs if m['ascii'] == main_prov), max(provs, key=lambda m: m['area']))
        cat = 'large_town' if pop >= 400000 else 'town' if pop >= 250000 else 'rural'
        lines = ['state={', f'    id={sid}', f'    name="STATE_{sid}"', f'    manpower={int(pop * ratio)}', f'    state_category = {cat}',
                 '    history={', '        owner = ALB', '        add_core_of = ALB']
        lines += ['        victory_points = {', f'            {mainp["id"]} {vpv}', '        }']
        lines += ['    }', '    provinces={', '        ' + ' '.join(str(m['id']) for m in provs), '    }', '}']
        if res:
            lines.insert(lines.index('    history={'), '    resources={\n' + '\n'.join(f'        {k} = {v}' for k, v in res.items()) + '\n    }')
        w(f'history/states/{sid:03d}_state_{sid}.txt', '\n'.join(lines) + '\n')
        for m in provs: state_of_prov[m['id']] = sid
        vp_loc[mainp['id']] = (vpen, vpru)

    # ------------------------------------------------------------ strategic region 3 + clean region 2
    t = rd('map/strategicregions/2_adriatic.txt')
    m = re.search(r'(provinces\s*=\s*\{)([^}]*)(\})', t)
    ids = [int(x) for x in m.group(2).split() if int(x) not in REUSED]
    t = t[:m.start(2)] + '\n        ' + ' '.join(map(str, ids)) + '\n    ' + t[m.end(2):]
    w('map/strategicregions/2_adriatic.txt', t)
    y1 = rd('map/strategicregions/1_yugoslavia.txt')
    weather = re.search(r'    weather=\{.*\n\}', y1, re.S).group(0)
    region = ('strategic_region={\n    id=3\n    name="STRATEGIC_REGION_ALBANIA"\n    provinces={\n        '
              + ' '.join(str(m['id']) for m in sorted(PROV, key=lambda m: m['id'])) + '\n    }\n' + weather + '\n')
    w('map/strategicregions/3_albania.txt', region)

    # ------------------------------------------------------------ positions + unitstacks
    land_new = {m['id']: (RAST == i) for i, m in enumerate(PROV)}
    pos = {}
    for m in PROV:
        x, y = pole(land_new[m['id']]); pos[m['id']] = (x + 0.5, 2048 - (y + 0.5))
    lines = [l for l in rd('map/positions.txt').split('\n') if l.strip()]
    keep = [l for l in lines if int(l.split(';')[0]) not in REUSED and int(l.split(';')[0]) not in pos]
    for pid, (x, z) in pos.items(): keep.append('%d;%.2f;0.00;%.2f;0.00;0' % (pid, x, z))
    keep.sort(key=lambda l: int(l.split(';')[0]))
    w('map/positions.txt', '\n'.join(keep) + '\n')
    lines = [l for l in rd('map/unitstacks.txt').split('\n') if l.strip()]
    keep = [l for l in lines if int(l.split(';')[0]) not in REUSED and int(l.split(';')[0]) not in pos]
    n_existing = len(set(int(l.split(';')[0]) for l in keep))
    for pid, (x, z) in pos.items():
        for t_ in range(39): keep.append('%d;%d;%.2f;9.50;%.2f;0.00;0.00' % (pid, t_, x, z))
    keep.sort(key=lambda l: (int(l.split(';')[0]), int(l.split(';')[1])))
    w('map/unitstacks.txt', '\n'.join(keep) + '\n')

    # ------------------------------------------------------------ buildings
    h = np.array(Image.open(os.path.join(ROOT, 'map/heightmap.bmp'))).astype(float)
    prov_img = np.array(Image.open(os.path.join(ROOT, 'map/provinces.bmp')).convert('RGB'))
    key = (prov_img[..., 0].astype(np.int64) << 16) | (prov_img[..., 1].astype(np.int64) << 8) | prov_img[..., 2]
    import csv
    defs = [r for r in csv.reader(open(os.path.join(ROOT, 'map/definition.csv'), encoding='utf-8'), delimiter=';') if len(r) >= 8]
    col2id = {((int(r[1]) << 16) | (int(r[2]) << 8) | int(r[3])): int(r[0]) for r in defs}
    id_img = np.vectorize(col2id.get)(key) if False else None
    sea_ids = np.array([int(r[0]) for r in defs if r[4] == 'sea'])
    # sea province id per pixel via lookup table on colour
    lut_keys = np.array(sorted(col2id)); lut_ids = np.array([col2id[k] for k in lut_keys])
    idx = np.searchsorted(lut_keys, key); pid_img = lut_ids[idx]
    is_sea = np.isin(pid_img, sea_ids)
    coast = ndi.binary_dilation(is_sea, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
    old = [l for l in rd('map/buildings.txt').split('\n') if l.strip()]
    kept = []; dropped = 0
    for l in old:
        p = l.split(';')
        if len(p) >= 7 and p[6].isdigit() and int(p[6]) in REUSED: dropped += 1; continue
        kept.append(l)
    print('building rows dropped (pointed at sea provinces now covered by Albania):', dropped)
    COUNT = {'arms_factory': 6, 'industrial_complex': 7, 'supply_node': 5, 'anti_air_building': 4, 'bunker': 4,
             'special_project_facility_spawn': 4, 'air_base': 2, 'synthetic_refinery': 2, 'fuel_silo': 2, 'radar_station': 2,
             'rocket_site': 3, 'nuclear_reactor': 3, 'stronghold_network': 1, 'rocket_site_spawn': 1, 'nuclear_reactor_spawn': 1}
    NAVAL = {'naval_base_spawn': 2, 'floating_harbor': 1, 'naval_supply_hub': 1, 'naval_headquarters': 1, 'coastal_bunker': 2,
             'dockyard': 1, 'naval_base': 1}
    rows = []
    for cname, sid, *_ in COUNTIES:
        smask = np.zeros(h.shape, bool)
        for m in by_county[cname]: smask |= land_new[m['id']]
        inner = ndi.binary_erosion(smask, iterations=4)
        ys, xs = np.where(inner if inner.sum() > 200 else smask)
        def pick(n, mask_ys, mask_xs):
            sel = rng.choice(len(mask_ys), size=min(n, len(mask_ys)), replace=False)
            return [(int(mask_xs[i]), int(mask_ys[i])) for i in sel]
        for typ, n in COUNT.items():
            for (x, y) in pick(n, ys, xs):
                rows.append('%d;%s;%.2f;%.2f;%.2f;%.2f;0' % (sid, typ, x, max(9.5, h[y, x] / 10.0), 2048 - y, rng.uniform(0, 6.28)))
        cm = smask & coast
        if cm.any():
            cy_, cx_ = np.where(cm)
            for typ, n in NAVAL.items():
                for (x, y) in pick(n, cy_, cx_):
                    seap = 0
                    if typ in ('naval_base_spawn', 'floating_harbor', 'naval_base'):
                        win = pid_img[max(0, y - 2):y + 3, max(0, x - 2):x + 3]; cand = [v for v in win.ravel() if v in set(sea_ids.tolist())]
                        seap = collections.Counter(cand).most_common(1)[0][0] if cand else 0
                    rows.append('%d;%s;%.2f;9.50;%.2f;%.2f;%d' % (sid, typ, x, 2048 - y, -rng.uniform(0, 3.14), seap))
    w('map/buildings.txt', '\n'.join(kept + rows) + '\n')

    # ------------------------------------------------------------ supply, railways, airports
    tir = next(m for m in PROV if m['ascii'] == 'Tirane')['id']
    sn = rd('map/supply_nodes.txt').rstrip('\n') + '\n1 %d\n' % tir
    dur = next(m for m in PROV if m['ascii'] == 'Durres')['id']
    sn += '1 %d\n' % dur
    w('map/supply_nodes.txt', sn)
    # province adjacency inside Albania (4-neighbour)
    adj = collections.defaultdict(set)
    a = RAST
    for sl_a, sl_b in ((a[:, :-1], a[:, 1:]), (a[:-1, :], a[1:, :])):
        mm = (sl_a >= 0) & (sl_b >= 0) & (sl_a != sl_b)
        for u, v in set(zip(sl_a[mm].tolist(), sl_b[mm].tolist())): adj[u].add(v); adj[v].add(u)
    name2i = {m['ascii']: i for i, m in enumerate(PROV)}
    def path(src, dst):
        s, d = name2i[src], name2i[dst]; prev = {s: None}; q = collections.deque([s])
        while q:
            u = q.popleft()
            if u == d: break
            for v in adj[u]:
                if v not in prev: prev[v] = u; q.append(v)
        out = []; u = d
        while u is not None: out.append(u); u = prev[u]
        return out[::-1]
    def chain(names):
        seq = []
        for s, d in zip(names, names[1:]):
            p = path(s, d); seq += p if not seq else p[1:]
        return [PROV[i]['id'] for i in seq]
    rail = ''
    for lvl, names in ((3, ['Durres', 'Tirane', 'Elbasan', 'Librazhd', 'Pogradec']), (2, ['Durres', 'Kavaje', 'Lushnje', 'Fier', 'Vlore']),
                       (2, ['Durres', 'Kurbin', 'Lezhe', 'Shkoder']), (1, ['Fier', 'Berat', 'Kucove'])):
        try:
            ch = chain(names); rail += '%d %d %s\n' % (lvl, len(ch), ' '.join(map(str, ch)))
        except Exception as e:
            print('railway skipped', names, e)
    w('map/railways.txt', rd('map/railways.txt').rstrip('\n') + '\n' + rail)
    w('map/airports.txt', rd('map/airports.txt').rstrip('\n') + '\n%d = { %d }\n' % (CAPITAL_STATE, tir))

    # ------------------------------------------------------------ country
    w('common/country_tags/YGwar_tags.txt', rd('common/country_tags/YGwar_tags.txt').rstrip('\n') + '\nALB = "countries/ALB - Albania.txt"\n')
    w('common/countries/ALB - Albania.txt', 'graphical_culture = eastern_european_gfx\ngraphical_culture_2d = eastern_european_2d\ncolor = rgb { 170 20 60 }\ncolor_ui = rgb { 170 20 60 }\n')
    w('common/countries/colors.txt', rd('common/countries/colors.txt').rstrip('\n') + '\n\nALB = {\n    color = rgb { 170 20 60 }\n    color_ui = rgb { 170 20 60 }\n}\n')
    hist = f'''capital = {CAPITAL_STATE}
oob = "ALB_OOB"
set_research_slots = 2
set_stability = 0.50
set_war_support = 0.35
set_politics = {{
    ruling_party = communism
    last_election = "1987.2.1"
    election_frequency = 48
    elections_allowed = no
}}
set_popularities = {{
    communism = 55
    democratic = 30
    neutrality = 15
}}
add_ideas = {{
    partial_mobilization
    export_focus
    extensive_conscription
}}
set_technology = {{
    infantry_weapons = 1
    infantry_weapons1 = 1
    tech_support = 1
    tech_engineers = 1
    tech_recon = 1
    gw_artillery = 1
}}
recruit_character = ALB_YGwar_leader
'''
    w('history/countries/ALB - Albania.txt', hist)
    div = ['# ALB_OOB - one infantry division per county, in its main province', '',
           'division_template = {', '\tname = "Піхотна дивізія"', '\tregiments = {']
    for x_ in range(2):
        for y_ in range(3): div.append(f'\t\tinfantry = {{ x = {x_} y = {y_} }}')
    div += ['\t}', '\tsupport = {', '\t\tengineer = { x = 0 y = 0 }', '\t}', '}', '', 'units = {']
    for n, (cname, sid, *_r) in enumerate(COUNTIES, 1):
        mainp = next((m for m in by_county[cname] if m['ascii'] == _r[4]), max(by_county[cname], key=lambda m: m['area']))
        div += ['\tdivision = {', f'\t\tname = "{n}-ша піхотна дивізія"', f'\t\tlocation = {mainp["id"]}',
                '\t\tdivision_template = "Піхотна дивізія"', '\t\tstart_experience_factor = 0.2', '\t\tstart_equipment_factor = 1.0', '\t}']
    div.append('}')
    w('history/units/ALB_OOB.txt', '\n'.join(div) + '\n')
    # leader
    lead = rd('common/characters/YGwar_leaders.txt').rstrip()
    assert lead.endswith('}')
    lead = lead[:-1].rstrip() + '''
    ALB_YGwar_leader = {
        name = ALB_YGwar_leader
        country_leader = {
            ideology = stalinism
            expire = "2100.1.1"
            id = -1
        }
    }
}
'''
    w('common/characters/YGwar_leaders.txt', lead)
    ai = rd('common/ai_strategy/YGwar_ai.txt').rstrip('\n') + '''
YGwar_ai_ALB = {
	enable = { tag = ALB }
	abort = { always = no }
	ai_strategy = { type = befriend id = "KOS" value = 150 }
	ai_strategy = { type = befriend id = "MAC" value = 50 }
	ai_strategy = { type = antagonize id = "SER" value = 50 }
}
'''
    w('common/ai_strategy/YGwar_ai.txt', ai)
    un = rd('common/units/names/YGwar_unit_names.txt').rstrip('\n') + '''

ALB = {
	air_wing_names_template = YGWAR_AIR_WING_NAME
	fleet_names_template = YGWAR_FLEET_NAME
	task_force_names_template = YGWAR_TASK_FORCE_NAME
}
'''
    w('common/units/names/YGwar_unit_names.txt', un)
    mio = rd('common/military_industrial_organization/organizations/00_generic_organization.txt')
    mio, n_mio = re.subn(r'(?m)^([ \t]*)tag = HRZ[ \t]*$', lambda m: m.group(0) + '\n' + m.group(1) + 'tag = ALB', mio)
    w('common/military_industrial_organization/organizations/00_generic_organization.txt', mio)
    print('MIO tag lists extended:', n_mio)

    # ------------------------------------------------------------ localisation
    BOM = '\ufeff'
    en = [BOM + 'l_english:', ' ALB_YGwar_leader:0 "Ramiz Alia"', ' STRATEGIC_REGION_ALBANIA:0 "Albania"']
    ru = [BOM + 'l_russian:', ' ALB_YGwar_leader:0 "Рамиз Алия"', ' STRATEGIC_REGION_ALBANIA:0 "Албания"']
    w('localisation/english/YGwar_albania_l_english.yml', '\n'.join(en) + '\n')
    w('localisation/russian/YGwar_albania_l_russian.yml', '\n'.join(ru) + '\n')
    sen = [BOM + 'l_english:']; sru = [BOM + 'l_russian:']
    for cname, sid, en_, ru_, *_r in COUNTIES:
        sen.append(f' STATE_{sid}:0 "{en_}"'); sru.append(f' STATE_{sid}:0 "{ru_}"')
    for pid, (e_, r_) in sorted(vp_loc.items()):
        sen.append(f' VICTORY_POINTS_{pid}:0 "{e_}"'); sru.append(f' VICTORY_POINTS_{pid}:0 "{r_}"')
    w('localisation/replace/YGwar_albania_names_l_english.yml', '\n'.join(sen) + '\n')
    w('localisation/replace/YGwar_albania_names_l_russian.yml', '\n'.join(sru) + '\n')
    json.dump({m['id']: state_of_prov[m['id']] for m in PROV}, open(os.path.join(IN, 'province_state.json'), 'w'))
    print('done. positions rows for', len(pos), 'provinces; unitstacks existing provinces kept:', n_existing)


if __name__ == '__main__':
    main()
