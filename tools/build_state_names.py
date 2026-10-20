#!/usr/bin/env python3
"""Rebuild the state / victory-point name localisation from tools/state_names.csv.

Usage (from the mod root, i.e. the folder that contains descriptor.mod):
    python tools/build_state_names.py

Edit tools/state_names.csv first if a name is wrong (columns: state_id; vp_province;
state_name_ru; state_name_en; vp_city_ru; vp_city_en; ...), then run the script again.
Writes:  localisation/replace/YGwar_state_names_l_russian.yml
         localisation/replace/YGwar_state_names_l_english.yml
"""
import csv, os, sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(root, 'tools', 'state_names.csv')
out_dir = os.path.join(root, 'localisation', 'replace')
os.makedirs(out_dir, exist_ok=True)

def esc(s):
    return s.replace('"', "'")

rows = list(csv.reader(open(src, encoding='utf-8-sig'), delimiter=';'))[1:]
ru, en = ['l_russian:'], ['l_english:']
for r in rows:
    sid, vp, st_ru, st_en, vp_ru, vp_en = r[:6]
    ru.append(f' STATE_{sid}:0 "{esc(st_ru)}"')
    en.append(f' STATE_{sid}:0 "{esc(st_en)}"')
for r in rows:
    sid, vp, st_ru, st_en, vp_ru, vp_en = r[:6]
    ru.append(f' VICTORY_POINTS_{vp}:0 "{esc(vp_ru)}"')
    en.append(f' VICTORY_POINTS_{vp}:0 "{esc(vp_en)}"')

for name, lines in (('YGwar_state_names_l_russian.yml', ru), ('YGwar_state_names_l_english.yml', en)):
    with open(os.path.join(out_dir, name), 'w', encoding='utf-8-sig', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    print('wrote', os.path.join('localisation', 'replace', name), len(lines) - 1, 'keys')
