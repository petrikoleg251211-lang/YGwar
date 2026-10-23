#!/usr/bin/env python3
"""Static checks (no game launch): braces, referenced ideas/characters/events/effects exist,
loc keys exist, focus graph, duplicate IDs. Run from repo root: python tools/check_yug_content.py"""
import re, glob, os, sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
def rd(p): return open(p,encoding='utf-8-sig').read()
def strip(t): return re.sub(r'#.*','',t)
problems=[]
files=[f for f in glob.glob('**/*.txt',recursive=True) if not f.startswith(('tools','.git'))]
for f in files:
    t=strip(rd(f))
    if t.count('{')!=t.count('}'): problems.append(f'brace mismatch {f}: {t.count("{")} vs {t.count("}")}')
# loc keys
loc={}
for f in glob.glob('localisation/**/*.yml',recursive=True):
    lang='ru' if 'russian' in f else 'en' if 'english' in f else 'x'
    for ln in rd(f).splitlines():
        m=re.match(r'\s+([A-Za-z0-9_.\-]+):\d*\s+"',ln)
        if m: loc.setdefault((lang,m.group(1)),[]).append(f)
for k,v in loc.items():
    if len(v)>1 and len(set(v))>1: problems.append(f'duplicate loc key {k} in {v}')
def haveloc(k): return ('en',k) in loc and ('ru',k) in loc
# focuses
foc_ids=[];foc_txt=''
for f in glob.glob('common/national_focus/*.txt'):
    if 'tech_trigger_stubs' in f or 'generic_focus' in f: continue  # hidden technical trees, never shown to players
    t=strip(rd(f)); foc_txt+=t
    foc_ids+=re.findall(r'\n\s*id = ([A-Za-z0-9_]+)\s*\n\s*icon',t)
if len(foc_ids)!=len(set(foc_ids)): problems.append('duplicate focus ids')
for i in foc_ids:
    if not (haveloc(i) and haveloc(i+'_desc')): problems.append(f'focus without full loc: {i}')
# ideas
idea_defs=set()
for f in glob.glob('common/ideas/*.txt'): idea_defs|=set(re.findall(r'\n\t\t([A-Za-z0-9_]+) = \{',rd(f)))
all_txt=''.join(strip(rd(f)) for f in files)
used_ideas=set(re.findall(r'(?:add_ideas|remove_ideas|has_idea|add_idea|remove_idea) = \{?\s*([A-Za-z0-9_]+)',all_txt))
for m in re.findall(r'add_ideas = \{([^}]*)\}',all_txt):
    used_ideas|=set(m.split())
for i in sorted(used_ideas):
    if i.startswith('YUG_') and i not in idea_defs: problems.append(f'idea used but not defined: {i}')
for i in sorted(x for x in idea_defs if x.startswith('YUG_')):
    if not haveloc(i): problems.append(f'idea without loc: {i}')
# characters
chars=set(re.findall(r'\n    ([A-Za-z0-9_]+) = \{\n        name',rd('common/characters/YGwar_leaders.txt')))
for c in set(re.findall(r'(?:recruit_character|promote_character) = ([A-Za-z0-9_]+)',all_txt)):
    if c not in chars: problems.append(f'character not defined: {c}')
for c in chars:
    if not haveloc(c): problems.append(f'character without loc: {c}')
# events
ev_defs=set(re.findall(r'\n\s*id = (YGwar\.\d+)',all_txt))
for e in set(re.findall(r'country_event = \{ id = (YGwar\.\d+)',all_txt)):
    if e not in ev_defs: problems.append(f'event fired but not defined: {e}')
fired=set(re.findall(r'country_event = \{ id = (YGwar\.\d+)',all_txt))|{'YGwar.1'}
for e in sorted(ev_defs):
    if e not in fired: problems.append(f'event never fired: {e}')
    for suf in ('.t','.d','.a'):
        if not haveloc(e+suf): problems.append(f'event loc missing: {e}{suf}')
# scripted effects
se_defs=set()
for f in glob.glob('common/scripted_effects/*.txt'): se_defs|=set(re.findall(r'^([A-Za-z0-9_]+) = \{',strip(rd(f)),re.M))
for s in set(re.findall(r'\b(YGwar_[A-Za-z0-9_]+) = (?:yes|\{ VAL)',all_txt)):
    if s not in se_defs: problems.append(f'scripted effect not defined: {s}')
# decisions
for f in glob.glob('common/decisions/YGwar_decisions.txt'):
    t=strip(rd(f))
    for d in re.findall(r'\n\t([A-Za-z0-9_]+) = \{\n\t\ticon',t):
        if not haveloc(d): problems.append(f'decision without loc: {d}')
for c in re.findall(r'\n([A-Za-z0-9_]+_category) = \{',rd('common/decisions/categories/YGwar_categories.txt')):
    if not haveloc(c): problems.append(f'category without loc: {c}')
# states / cores
for f in glob.glob('history/states/*.txt'):
    t=rd(f)
    if 'owner = YUG' not in t: problems.append(f'state not owned by YUG at start: {f}')
# state integrity
import json as _j
owner={}
for f in glob.glob('history/states/*.txt'):
    tt=rd(f); sid=int(re.search(r'id\s*=\s*(\d+)',tt).group(1))
    for p in re.search(r'provinces\s*=\{([^}]*)\}',tt).group(1).split():
        if p in owner: problems.append(f'province {p} in states {owner[p]} and {sid}')
        owner[p]=sid
    if os.path.basename(f)!='%03d_state_%d.txt'%(sid,sid): problems.append('state file name mismatch '+f)
    if not haveloc('STATE_%d'%sid): problems.append('state without name: %d'%sid)
defs=set(l.split(';')[0] for l in rd('map/definition.csv').splitlines())
for p in owner:
    if p not in defs: problems.append(f'province {p} not in definition.csv')
sa=set(int(x) for m in re.finditer(r'states=\{\s*([\d\s]+?)\s*\}',rd('map/supplyareas/00_supplyareas.txt')) for x in m.group(1).split())
allst=set(owner.values())
if sa!=allst: problems.append(f'supply areas vs states differ: {sorted(sa^allst)}')
caps=_j.load(open('tools/_capitals.json'))
for tag,c in caps.items():
    h=glob.glob('history/countries/%s - *.txt'%tag)[0]
    if f'capital = {c}' not in rd(h): problems.append(f'capital mismatch {tag}')
    if c not in allst: problems.append(f'capital state missing {tag} {c}')
print('states:',len(allst),'provinces in states:',len(owner))
print('focuses:',len(foc_ids),' YUG:',sum(1 for i in foc_ids if i.startswith('YUG_')),' events:',len(ev_defs),' loc keys(en):',sum(1 for k in loc if k[0]=='en'))
print('\n'.join(problems) if problems else 'NO PROBLEMS FOUND by static checks')
sys.exit(1 if problems else 0)
