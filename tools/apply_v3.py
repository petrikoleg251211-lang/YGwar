#!/usr/bin/env python3
"""pass2 v2 -> v3: realistic Slovenian border (user's hand-edited map 104479.png), Bosnia sea access only via Neum.
Run from the mod root. Needs numpy, scipy, Pillow. Expects tools/_v3_inputs/ (m14_svn.npy, m14_cro.npy: the split of province 14).
Documentation of what was done; the archive already contains the result, do NOT run it again on the v3 files."""
import re, os, csv, json, glob, collections
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
NEWP=1245
# ---------- 1. parse old states
old={}
for f in glob.glob('history/states/*.txt'):
    t=open(f,encoding='utf-8').read()
    i=int(re.search(r'\bid=(\d+)',t).group(1))
    old[i]=dict(man=int(re.search(r'manpower=(\d+)',t).group(1)),cat=re.search(r'state_category = (\w+)',t).group(1),
        cores=re.findall(r'add_core_of = (\w+)',t),
        vps=[(int(a),int(b)) for a,b in re.findall(r'^\s+(\d+) (\d+)\s*$',re.search(r'victory_points = \{(.*?)\}',t,re.S).group(1),re.M)] if 'victory_points' in t else [],
        provs=[int(x) for x in re.search(r'provinces=\{([^}]*)\}',t).group(1).split()])
old_state={p:s for s,d in old.items() for p in d['provs']}
vp_of={p:v for d in old.values() for p,v in d['vps']}
NEWVP={24:('Kranj','Крань'),48:('Trbovlje','Трбовле'),77:('Postojna','Постойна'),92:('Kočevje','Кочевье'),114:('Koper','Копер')}   # states that had no city of their own
for q in NEWVP: vp_of[q]=1
# ---------- 2. new assignment
new_state=dict(old_state)
SVN={1:[1,2,4,11],69:[3,6,8,9,17,16,NEWP],96:[5,7,10,12],23:[20,22,23,27,28,43],61:[40,48,51,55],93:[33,34,59,66],
     63:[38,39,52,53,50,26,61],116:[21,24,32],10:[15,18,19,41,49,71],29:[64,76,77,106],117:[80,114],60:[56,65,70,75],118:[85,92,101,102]}
for s,ps in SVN.items():
    for p in ps: new_state[p]=s
for p,s in {13:72,35:35,54:35,14:35,93:14,104:36,427:104}.items(): new_state[p]=s   # -> Croatia
old_state[NEWP]=old_state[14]
assert set(old)==set(new_state.values()),'a state would become empty'
# ---------- 3. split province 14 in provinces.bmp
svn=np.load('tools/_v3_inputs/m14_svn.npy'); cro=np.load('tools/_v3_inputs/m14_cro.npy')
im=np.array(Image.open('map/provinces.bmp').convert('RGB'))
rows=[r for r in csv.reader(open('map/definition.csv'),delimiter=';') if r]
cols={(int(r[1]),int(r[2]),int(r[3])) for r in rows}
newcol=next((14,0,k) for k in range(1,256) if (14,0,k) not in cols)
im[svn]=newcol
Image.fromarray(im).save('map/provinces.bmp',format='BMP')
d14=[r for r in rows if r[0]=='14'][0]
open('map/definition.csv','a').write(';'.join([str(NEWP),str(newcol[0]),str(newcol[1]),str(newcol[2])]+d14[4:])+'\n')
def centre(m):
    ys,xs=np.where(m); cx,cy=xs.mean(),ys.mean(); j=np.argmin((xs-cx)**2+(ys-cy)**2); return xs[j]+0.5,2048-(ys[j]+0.5)
(cx_s,cz_s),(cx_c,cz_c)=centre(svn),centre(cro)
L=open('map/positions.txt').read().splitlines()
for i,l in enumerate(L):
    f=l.split(';')
    if f[0]=='14': f[1]=f'{cx_c:.2f}'; f[3]=f'{cz_c:.2f}'; L[i]=';'.join(f)
L.append(f'{NEWP};{cx_s:.2f};0.00;{cz_s:.2f};0.00;0'); open('map/positions.txt','w').write('\n'.join(L)+'\n')
U=open('map/unitstacks.txt').read().splitlines(); out=[]; add=[]
for l in U:
    f=l.split(';')
    if f[0]=='14':
        f[2]=f'{cx_c:.2f}'; f[4]=f'{cz_c:.2f}'; l=';'.join(f)
        g=list(f); g[0]=str(NEWP); g[2]=f'{cx_s:.2f}'; g[4]=f'{cz_s:.2f}'; add.append(';'.join(g))
    out.append(l)
open('map/unitstacks.txt','w').write('\n'.join(out+add)+'\n')
p='map/strategicregions/1_yugoslavia.txt'; t=open(p,encoding='utf-8').read()
t=re.sub(r'(provinces=\{\s*)([\d\s]+?)(\s*\})',lambda m:m.group(1)+' '.join(m.group(2).split()+[str(NEWP)])+m.group(3),t,count=1); open(p,'w',encoding='utf-8').write(t)
# ---------- 4. manpower (equal share per province of the old state; province 14 split by area)
share={p:old[s]['man']/len(old[s]['provs']) for p,s in old_state.items() if p!=NEWP}
a_s,a_c=int(svn.sum()),int(cro.sum()); s14=share[14]; share[NEWP]=s14*a_s/(a_s+a_c); share[14]=s14*a_c/(a_s+a_c)
tot_old=sum(d['man'] for d in old.values())
new={s:[] for s in old}
for p,s in new_state.items(): new[s].append(p)
man={s:sum(share[p] for p in ps) for s,ps in new.items()}
k=tot_old/sum(man.values()); man={s:int(round(v*k)) for s,v in man.items()}; big=max(man,key=man.get); man[big]+=tot_old-sum(man.values())
# Slovenian manpower: the equal-share rule distorts reshaped states, so the Slovenian total is redistributed by rough 1991 census
# population of the matching regions (thousands, from memory, +-10%; tune in history/states if needed)
POP={1:128,69:320,96:75,23:215,61:47,93:70,63:470,116:190,10:118,29:52,117:100,60:85,118:55}
Ts=sum(man[s] for s in POP); man.update({s:int(round(Ts*POP[s]/sum(POP.values()))) for s in POP}); man[63]+=Ts-sum(man[s] for s in POP)
# ---------- 5. write states
for f in glob.glob('history/states/*.txt'): os.remove(f)
for s in sorted(new):
    ps=sorted(new[s]); vps=[(p,vp_of[p]) for p in ps if p in vp_of]
    L=['state={',f'    id={s}',f'    name="STATE_{s}"',f'    manpower={man[s]}',f'    state_category = {old[s]["cat"]}','    history={','        owner = YUG']
    L+=[f'        add_core_of = {c}' for c in old[s]['cores']]
    if vps: L+=['        victory_points = {']+[f'            {p} {v}' for p,v in vps]+['        }']
    L+=['    }','    provinces={','        '+' '.join(map(str,ps)),'    }','}']
    open('history/states/%03d_state_%d.txt'%(s,s),'w',encoding='utf-8').write('\n'.join(L)+'\n')
print('states',len(new),'manpower total',sum(man.values()),'(was',tot_old,')')
# ---------- 6. buildings / airports / rocketsites follow the province position
key=(im[:,:,0].astype(np.int64)<<16)|(im[:,:,1].astype(np.int64)<<8)|im[:,:,2].astype(np.int64)
lut={(int(r[1])<<16)|(int(r[2])<<8)|int(r[3]):int(r[0]) for r in csv.reader(open('map/definition.csv'),delimiter=';') if r}
uk,inv=np.unique(key,return_inverse=True); pid=np.array([lut.get(int(k),-1) for k in uk])[inv].reshape(key.shape)
B=[];moved=0
for l in open('map/buildings.txt').read().splitlines():
    if not l.strip(): continue
    f=l.split(';'); x=int(float(f[2])); y=int(2048-float(f[4])); pr=int(pid[min(max(y,0),2047),min(max(x,0),2047)])
    if pr in new_state and int(f[0])==old_state.get(pr) and old_state[pr]!=new_state[pr]: f[0]=str(new_state[pr]); moved+=1
    B.append(';'.join(f))
B.sort(key=lambda l:int(l.split(';')[0])); open('map/buildings.txt','w').write('\n'.join(B)+'\n')
have={int(l.split(';')[0]) for l in B}; print('building rows re-keyed:',moved,'| states without building rows:',sorted(set(new)-have))
for fn in ('airports','rocketsites'):
    oldp={int(a):int(b) for a,b in re.findall(r'(\d+)\s*=\s*\{\s*(\d+)\s*\}',open(f'map/{fn}.txt').read())}
    L=[];ch=0
    for s in sorted(new):
        pv=oldp.get(s)
        if pv not in new[s]: pv=sorted(new[s])[0]; ch+=1
        L.append(f'{s} = {{ {pv} }}')
    open(f'map/{fn}.txt','w').write('\n'.join(L)+'\n'); print(fn,'changed',ch)
# ---------- 7. state names (Slovenia) and new victory-point names
NAMES={1:('Pomurje','Помурье'),69:('Podravje','Подравье'),96:('Koroška','Корушка'),23:('Savinjska','Савинья'),61:('Zasavje','Засавье'),
 93:('Posavje','Посавье'),63:('Ljubljana','Любляна'),116:('Gorenjska','Горенская'),10:('Goriška','Горишка'),29:('Notranjska','Нотраньска'),
 117:('Obalno-kraška','Побережье и Карст'),60:('Dolenjska','Доленьска'),118:('Kočevje and Bela Krajina','Кочевье и Бела-Краина')}
for fn,ix in (('YGwar_state_names_l_english.yml',0),('YGwar_state_names_l_russian.yml',1)):
    p='localisation/replace/'+fn; t=open(p,encoding='utf-8-sig').read()
    for s,nm in NAMES.items(): t=re.sub(rf' STATE_{s}:0 ".*"',f' STATE_{s}:0 "{nm[ix]}"',t)
    t=re.sub(r' STATE_104:0 ".*"',' STATE_104:0 "%s"'%('Dubrovnik','Дубровник')[ix],t)
    t=t.rstrip('\n')+'\n'+''.join(f' VICTORY_POINTS_{q}:0 "{n[ix]}"\n' for q,n in NEWVP.items())
    open(p,'w',encoding='utf-8-sig').write(t)
# ---------- 8. tools data
data=json.load(open('tools/state_split_final.json'))
for p,s in new_state.items():
    tag,zone=data['state_zone'][str(s)]; data['provinces'][str(p)]=[s,tag,zone]
json.dump(data,open('tools/state_split_final.json','w'),ensure_ascii=False)
pc=json.load(open('tools/province_coords.json'))
c14=[d for d in pc if d['id']==14][0]; n=dict(c14); n['id']=NEWP; n['x']=round(cx_s,2); n['z']=round(cz_s,2); c14['x']=round(cx_c,2); c14['z']=round(cz_c,2); pc.append(n)
json.dump(pc,open('tools/province_coords.json','w'))
print('new province',NEWP,'colour',newcol,'areas svn/cro',a_s,a_c)
