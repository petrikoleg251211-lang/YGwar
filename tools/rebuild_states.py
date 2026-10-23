#!/usr/bin/env python3
"""Rebuilds history/states from tools/state_split_final.json (province -> [state, tag, claim]) using the ORIGINAL
state files from git HEAD (manpower, category, victory points). Also: supply areas, state-name localisation,
state_republic_map.csv. Re-runnable: always starts from HEAD originals. Run from anywhere; needs git."""
import json, re, os, glob, subprocess, collections, csv
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
data=json.load(open('tools/state_split_final.json'))
prov={int(p):v for p,v in data['provinces'].items()}
caps=data['capitals']; sz={int(s):tuple(z) for s,z in data['state_zone'].items()}
def head(path): return subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT).decode('utf-8')
orig={}   # old state id -> dict
prov_origin={}
for i in range(1,101):
    fn=glob.glob('history/states/%03d_*.txt'%i)[0]; t=head(fn.replace('\\','/'))
    m=int(re.search(r'manpower\s*=\s*(\d+)',t).group(1)); cat=re.search(r'state_category\s*=\s*(\w+)',t).group(1)
    ps=[int(x) for x in re.search(r'provinces\s*=\s*\{([^}]*)\}',t).group(1).split()]
    vps=[(int(a),int(b)) for a,b in re.findall(r'(\d+)\s+(\d+)\s*\n',re.search(r'victory_points\s*=\s*\{([^}]*)\}',t).group(1)+'\n')]
    orig[i]=dict(manpower=m,cat=cat,provs=ps,vps=vps)
    for p in ps: prov_origin[p]=i
st=collections.defaultdict(list)
for p,(s,t,c) in prov.items(): st[s].append(p)
assert set(prov)==set(prov_origin),'province sets differ'
vp_of={p:v for o in orig.values() for p,v in o['vps']}
for fn in glob.glob('history/states/*.txt'): os.remove(fn)
parent={}
for s in st:
    if s>100:
        c=collections.Counter(prov_origin[p] for p in st[s]); parent[s]=c.most_common(1)[0][0]
total=0
for s in sorted(st):
    ps=sorted(st[s]); tag,claim=sz[s]
    man=sum(orig[prov_origin[p]]['manpower']/len(orig[prov_origin[p]]['provs']) for p in ps); man=max(int(round(man)),1000)
    cat=orig[s]['cat'] if s in orig else orig[parent[s]]['cat']
    vps=[(p,vp_of[p]) for p in ps if p in vp_of]
    cores=['YUG',tag]+([claim] if claim else [])
    L=['state={',f'    id={s}',f'    name="STATE_{s}"',f'    manpower={man}',f'    state_category = {cat}','    history={','        owner = YUG']
    L+=[f'        add_core_of = {c}' for c in cores]
    if vps: L+=['        victory_points = {']+[f'            {p} {v}' for p,v in vps]+['        }']
    L+=['    }','    provinces={','        '+' '.join(map(str,ps)),'    }','}']
    name=glob.glob('history/states/%03d_*.txt'%s)
    open('history/states/%03d_state_%d.txt'%(s,s),'w',encoding='utf-8').write('\n'.join(L)+'\n'); total+=man
print('states written:',len(st),' manpower total',total,'(orig',sum(o['manpower'] for o in orig.values()),')')
# supply areas: new states join the parent's area
p='map/supplyareas/00_supplyareas.txt'; t=head(p)
def fix(m):
    ids=[int(x) for x in m.group(2).split()]; add=[s for s in sorted(parent) if parent[s] in ids]
    return m.group(1)+' '.join(map(str,ids+add))+m.group(3)
t2=re.sub(r'(states=\{\s*)([\d\s]+?)(\s*\})',fix,t); open(p,'w',encoding='utf-8').write(t2)
cnt=len(set(int(x) for m in re.finditer(r'states=\{\s*([\d\s]+?)\s*\}',t2) for x in m.group(1).split()))
print('supply areas cover',cnt,'states')
# names
tagen={'SVN':'Slovenia','CRO':'Croatia','BOS':'Bosnia','SER':'Serbia','VOJ':'Vojvodina','KOS':'Kosovo','MNT':'Montenegro','MAC':'Macedonia'}
tagru={'SVN':'Словения','CRO':'Хорватия','BOS':'Босния','SER':'Сербия','VOJ':'Воеводина','KOS':'Косово','MNT':'Черногория','MAC':'Македония'}
claimen={'RSK':'Serb-held','RSB':'Serb-held','HRZ':'Croat-held'}; claimru={'RSK':'сербский контроль','RSB':'сербский контроль','HRZ':'хорватский контроль'}
NEWNAMES={116:('Slovenia North-East (border)','Северо-восток Словении (граница)'),117:('Slovenian Istria','Словенская Истрия'),118:('Ilirska Bistrica','Илирска-Бистрица'),119:('Neum','Неум'),120:('Eastern Slavonia (border)','Восточная Славония (граница)')}
oldtag={int(k):v for k,v in json.load(open('tools/_original_state_tags.json')).items()}
for lang,fn in (('english','YGwar_state_names_l_english.yml'),('russian','YGwar_state_names_l_russian.yml')):
    path=f'localisation/replace/{fn}'; txt=head(path)
    names={int(a):b for a,b in re.findall(r' STATE_(\d+):0 "(.*)"',txt)}
    d=tagen if lang=='english' else tagru; cl=claimen if lang=='english' else claimru
    ren=0
    for s in sorted(st):
        tag,claim=sz[s]
        if s in orig:
            if oldtag.get(s)!=tag: names[s]=f'{d[tag]} {s}'; ren+=1
        else:
            names[s]=f'{names[parent[s]]} ({cl.get(claim,d[tag])})'
    for sid,(en,ru) in NEWNAMES.items(): names[sid]=en if lang=='english' else ru
    names[115]=('Sarajevo' if lang=='english' else 'Сараево')
    names[40]=('Belgrade' if lang=='english' else 'Белград')   # capital of Serbia/YUG sits in this state per the reference map
    out='\ufeffl_%s:\n'%lang+''.join(f' STATE_{s}:0 "{names[s]}"\n' for s in sorted(names))
    vp=[l for l in txt.splitlines() if 'VICTORY_POINTS' in l]
    open(path,'w',encoding='utf-8').write(out+'\n'.join(vp)+'\n')
    print(lang,'names:',len(names),'renamed (region changed):',ren)
# repo table for effects
by=collections.defaultdict(list)
for s,(t,c) in sz.items(): by[t].append(s)
cl=collections.defaultdict(list)
for s,(t,c) in sz.items():
    if c: cl[c].append(s)
with open('tools/state_republic_map.csv','w',encoding='utf-8',newline='') as f:
    f.write('tag;state_ids;extra_note\n')
    for t in ['SVN','CRO','BOS','SER','VOJ','KOS','MNT','MAC']: f.write(f'{t};{",".join(map(str,sorted(by[t])))};capital={caps[t]}\n')
    for t in ['RSK','RSB','HRZ']: f.write(f'{t};{",".join(map(str,sorted(cl[t])))};claim zone, capital={caps[t]}\n')
json.dump(caps,open('tools/_capitals.json','w'))

# ---- map/buildings.txt, airports.txt, rocketsites.txt are keyed by STATE id -> re-key by province position
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
im=np.array(Image.open('map/provinces.bmp').convert('RGB')).astype(np.int64)
key=im[:,:,0]*65536+im[:,:,1]*256+im[:,:,2]
lut={}
for r in csv.reader(open('map/definition.csv',encoding='utf-8',errors='ignore'),delimiter=';'):
    if len(r)>=4 and r[0].isdigit(): lut[int(r[1])*65536+int(r[2])*256+int(r[3])]=int(r[0])
uk,inv=np.unique(key,return_inverse=True); pidmap=np.array([lut.get(int(k),-1) for k in uk])[inv].reshape(key.shape)
H=pidmap.shape[0]
final_of={p:v[0] for p,v in prov.items()}
main_of={s:collections.Counter(final_of[p] for p in orig[s]['provs']).most_common(1)[0][0] for s in orig}
out=[];moved=0;fallback=0
for l in head('map/buildings.txt').splitlines():
    if not l.strip(): continue
    f=l.split(';'); s0=int(f[0]); x=int(float(f[2])); y=int(H-float(f[4]))
    p=int(pidmap[min(max(y,0),H-1),min(max(x,0),H-1)])
    if p in final_of and prov_origin.get(p)==s0: new=final_of[p]
    else: new=main_of[s0]; fallback+=1
    if new!=s0: moved+=1
    f[0]=str(new); out.append(';'.join(f))
out.sort(key=lambda l:int(l.split(';')[0]))
open('map/buildings.txt','w',encoding='utf-8',newline='\n').write('\n'.join(out)+'\n')
have=set(int(l.split(';')[0]) for l in out)
print('building rows:',len(out),'re-keyed to another state:',moved,'(fallback for coastal/edge rows:',fallback,') states without any building row:',sorted(set(st)-have))
for fn in ('airports','rocketsites'):
    old={int(a):int(b) for a,b in re.findall(r'(\d+)\s*=\s*\{\s*(\d+)\s*\}',head(f'map/{fn}.txt'))}
    lines=[]
    for s in sorted(st):
        pv=old.get(s)
        if pv not in st[s]: pv=sorted(st[s])[0]
        lines.append(f'{s} = {{ {pv} }}')
    open(f'map/{fn}.txt','w',encoding='utf-8',newline='\n').write('\n'.join(lines)+'\n')
print('airports/rocketsites rewritten for',len(st),'states')
