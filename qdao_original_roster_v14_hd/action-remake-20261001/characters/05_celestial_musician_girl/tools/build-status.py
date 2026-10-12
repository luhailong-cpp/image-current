"""Scan native candidates with provenance; never auto-approve artwork."""
import json,hashlib,os,re
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
if (ROOT/'final/manifest.json').is_file():
    import subprocess,sys
    subprocess.run([sys.executable,str(ROOT/'tools/audit-final.py')],check=True)
    sys.exit(0)
OLD=ROOT.parents[2]/'run-correction-20260930/characters/05_celestial_musician_girl/generation/E'
SPEC={'run':(['N','NE','E','SE','S','SW','W','NW'],16),'hit':(['E','W'],6),'attack':(['E','W'],12),'cast':(['E','W'],16)}
def rel(p):return os.path.relpath(p,ROOT).replace('\\','/')
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
entries={};pending=[]
def add(a,d,f,p,r,origin):
    if not r.is_file():pending.append(rel(p));return
    doc=load(r);h=hashlib.sha256(p.read_bytes()).hexdigest()
    if doc.get('sha256')!=h:raise ValueError(f'SHA mismatch: {r}')
    with Image.open(p) as im:
        im.load();w,height=im.size;mode=im.mode;alpha=im.getchannel('A').getextrema() if mode=='RGBA' else None
    if min(w,height)<1024 or mode!='RGBA':raise ValueError(p)
    entries[(a,d,f)]={'action':a,'direction':d,'frame':f,'file':rel(p),'generationRecord':rel(r),'sha256':h,'nativeWidth':w,'nativeHeight':height,'mode':mode,'alphaExtrema':alpha,'origin':origin,'visualStatus':'候选已落盘；整段动作、根锚点和真实合成待验收','finalVisualPassed':False,'actualModel':doc.get('actualModel'),'actualQuality':doc.get('actualQuality')}
for f in (1,2,3,5):
    p=OLD/f'{f:02}-v1.png';add('run','E',f,p,Path(str(p)+'.generation.json'),'prior_committed_candidate')
for a in SPEC:
    latest={}
    for p in (ROOT/'staging'/a).rglob('*.png'):
        if a=='run':
            m=re.fullmatch(r'(\d+)-v(\d+)\.native\.png',p.name)
            if not m:continue
            d=p.parent.name;f,v=map(int,m.groups());r=ROOT/f'provenance/run/{d}{f:02}-v{v}.generation.json'
        else:
            m=re.fullmatch(r'([A-Z]+)-(\d+)-v(\d+)\.png',p.name)
            if not m:continue
            d=m[1];f=int(m[2]);v=int(m[3])
            r=Path(str(p)+'.generation.json') if a=='hit' else ROOT/f'provenance/{a}/{a}-{d}-{f:02}-v{v}.generation.json'
        if not r.is_file() and Path(str(p)+'.generation.json').is_file():r=Path(str(p)+'.generation.json')
        if not r.is_file() and (ROOT/f'provenance/{a}/{d}{f:02}-v{v}.generation.json').is_file():r=ROOT/f'provenance/{a}/{d}{f:02}-v{v}.generation.json'
        if d not in SPEC[a][0] or not 1<=f<=SPEC[a][1]:raise ValueError(p)
        if (d,f) not in latest or v>latest[(d,f)][0]:latest[(d,f)]=(v,p,r)
    for (d,f),(v,p,r) in latest.items():add(a,d,f,p,r,'new_builtin_generation')
explicitSelections={}
for selection in sorted((ROOT/'provenance').rglob('selection-*.json')):
    rows=load(selection)
    if not isinstance(rows,list):continue
    for row in rows:
        a=row['action'];d=row['direction'];f=int(row['frame']);p=ROOT/row['file'];r=ROOT/row['generationRecord']
        slot=(a,d,f)
        if slot in explicitSelections and explicitSelections[slot][0]!=p.resolve():
            raise ValueError(f'Conflicting explicit selections {slot}: {explicitSelections[slot]} versus {p} from {selection}')
        explicitSelections[slot]=(p.resolve(),str(selection))
        if not p.is_file():raise FileNotFoundError(p)
        origin='prior_committed_candidate' if 'run-correction-20260930' in str(p) else 'new_builtin_generation'
        add(a,d,f,p,r,origin)
        entry=entries[(a,d,f)]
        entry['reviewStatus']=row.get('reviewStatus','candidate')
        entry['visualStatus']=row.get('notes') or row.get('visualStatus') or '显式选帧；整段验收待完成'
        entry['selectionSource']=rel(selection)
selected=sorted(entries.values(),key=lambda e:(list(SPEC).index(e['action']),SPEC[e['action']][0].index(e['direction']),e['frame']))
save(ROOT/'candidate-selection.json',selected)
counts={a:sum(e['action']==a for e in selected) for a in SPEC}
new=sum(e['origin']=='new_builtin_generation' for e in selected)
sequences={}
for a,(directions,n) in SPEC.items():
    for d in directions:
        have=[e['frame'] for e in selected if e['action']==a and e['direction']==d]
        sequences[f'{a}/{d}']={'sourceCandidates':len(have),'expected':n,'missing':[f for f in range(1,n+1) if f not in have],'visualPassed':False}
successful=set()
for folder in ('staging','provenance'):
    for p in (ROOT/folder).rglob('*.generation.json'):
        doc=load(p)
        if doc.get('sha256'):successful.add(doc['sha256'])
status=load(ROOT/'STATUS.json')
status.update({'updatedAt':datetime.now(timezone.utc).isoformat(),'status':'in_progress_native_candidates','newCurrentCandidateSlots':new,'priorRetainedCandidateSlots':len(selected)-new,'selectedCandidateSlots':len(selected),'emptyCandidateSlots':196-len(selected),'candidateCounts':counts,'newSuccessfulGeneratedImages':len(successful),'supersededNewImages':len(successful)-new,'completeCandidateSequences':sum(not s['missing'] for s in sequences.values()),'sequences':sequences,'remaining':{a:len(d)*n-counts[a] for a,(d,n) in SPEC.items()},'filesWaitingForRecord':pending,'limitations':['候选源图不等于整段动作通过；正式1024导出和客户端验收尚未完成。','受击E03经浏览器白底和深底实看，未见查看器中的强烈杂色边；E05饱和杂色像素alpha仅1–4，其他帧继续按真实合成复核。','整段比例、固定根锚点、解剖持物和跑步异侧腿交替仍须核验。','真实缺口保持空槽，不以复制、镜像或插值填补。']})
save(ROOT/'STATUS.json',status)
previous=load(ROOT/'selected-files.json')
save(ROOT/'selected-files.json',{'files':selected,'excluded':previous.get('excluded',[])})
print(json.dumps({'selected':len(selected),'counts':counts,'shaChecksPassed':len(selected),'new':new,'retained':len(selected)-new,'candidateSequences':status['completeCandidateSequences'],'final':0,'waitingForRecord':pending},ensure_ascii=False))

