import json, hashlib, re
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

ROOT=Path('D:/work/image')
BASE=ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production'
PROD=BASE/'island-game-20261009'
AUDIT=BASE/'parallel-review-20261013/island-game-20261009'
OUT=AUDIT/'resume-v02/west'
OUT.mkdir(parents=True,exist_ok=True)
STAMP=datetime.now(timezone.utc).isoformat()
def norm(p): return str(Path(str(p))).replace('\\','/')
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,j):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
metadata=[]
def snapshot(zone,name):
    p=PROD/zone/name; data=p.read_bytes(); dest=OUT/'snapshots'/zone/name
    dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(data)
    metadata.append({'path':norm(p),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'mtimeNs':p.stat().st_mtime_ns,'snapshot':norm(dest)})
    return json.loads(data.decode('utf-8-sig'))
old={z:read(AUDIT/(z+'-audit-v01')/'inventory.json') for z in ['northwest','southwest']}
oldtiles={z:{t['tileId']:t for t in j['tiles']} for z,j in old.items()}
nw=snapshot('northwest','current-adopted-20261012.json')
nroot=snapshot('northwest','root-current-selection-20261012.json')
nwest=snapshot('northwest','west-current-selection-20261012.json')
nright=snapshot('northwest','right-current-selection-20261012.json')
nbase=snapshot('northwest','selected-native.json')
nprogress=snapshot('northwest','progress.json')
sw=snapshot('southwest','current-native-map.json')
sprogress=snapshot('southwest','progress.json')
sources={z:{} for z in old}
for z,j in old.items():
    for t in j['tiles']:
        sources[z][t['tileId']]={}
        for s in t.get('selectedSources',t.get('selectedCores',[])):
            sources[z][t['tileId']][(s['subrow'],s['subcolumn'])]={'path':norm(s['file']),'expectedSha256':s.get('sha256')}
def setcells(tile,cells):
    src={}
    for c in cells:
        stem=c['stem'];m=re.search(r'_s(\d+)_(\d+)_',stem)
        if not m: continue
        im=c.get('image',{}); p=im.get('path',str(PROD/'northwest/native'/f'{stem}.png'))
        src[(int(m[1]),int(m[2]))]={'path':norm(p),'expectedSha256':im.get('sha256')}
    sources['northwest'][tile]=src
for tile,d in nw.get('partialTiles',{}).items():
    if d.get('cells'): setcells(tile,d['cells'])
for d in (nroot,nright):
    for tile,t in d['tiles'].items(): setcells(tile,t.get('cells',[]))
for t in nwest.get('partialTiles',[]):
    if 'selectedNative' in t: setcells(t['tileId'],t['selectedNative'])
    elif t.get('selectedNativeStems'):
        setcells(t['tileId'],[{'stem':s} for s in t['selectedNativeStems']])
for tile,matrix in sw.items():
    if not re.fullmatch(r'r\d\d_c\d\d',tile) or not isinstance(matrix,list): continue
    oldbyfile={norm(s['file']):s for s in oldtiles['southwest'].get(tile,{}).get('selectedCores',[])}
    sources['southwest'][tile]={}
    for r,row in enumerate(matrix,1):
        for c,stem in enumerate(row,1):
            if stem:
                p=norm(PROD/'southwest/native'/f'{stem}.png')
                sources['southwest'][tile][(r,c)]={'path':p,'expectedSha256':oldbyfile.get(p,{}).get('sha256')}
candidates={'northwest':{t['tileId']:{'path':norm(t['image']['path']),'recordedSha256':t['image'].get('sha256')} for t in nw['tiles']},
            'southwest':{t:{'path':norm(d['path']),'recordedSha256':d.get('sha256')} for t,d in sw['candidateArtifacts'].items()}}
cache={}
def info(p):
    p=norm(p)
    if p not in cache:
        q=Path(p);s=q.stat(); h=sha(q)
        with Image.open(q) as im: dims=list(im.size)
        cache[p]={'path':p,'sha256':h,'bytes':s.st_size,'mtimeNs':s.st_mtime_ns,'dimensions':dims}
    return cache[p]
result={'startedAtUtc':STAMP,'scope':'NW/SW selected-input delta only; no generation or AI edits; production read-only','metadata':metadata,'zones':{},'newDiagnosticAssemblies':[],'visualReviews':[]}
for z in sources:
    ts=[]
    for tile,ss in sorted(sources[z].items()):
        ot=oldtiles[z].get(tile,{}); oldsrc={(s['subrow'],s['subcolumn']):s for s in ot.get('selectedSources',ot.get('selectedCores',[]))}
        selected=[]
        for (r,c),src in sorted(ss.items()):
            rec={**info(src['path']),'subrow':r,'subcolumn':c}; o=oldsrc.get((r,c))
            rec['oldSha256']=o.get('sha256') if o else None
            rec['change']='added' if not o else ('unchanged' if o.get('sha256')==rec['sha256'] else 'changed')
            rec['recordedSha256']=src.get('expectedSha256')
            rec['recordedHashMatches']=src.get('expectedSha256') in (None,rec['sha256'])
            selected.append(rec)
        candidate=None
        if tile in candidates[z]:
            ca=candidates[z][tile]; candidate={**info(ca['path']),'oldSha256':ot.get('sha256'),'recordedSha256':ca['recordedSha256']}
            candidate['unchangedFromAudit']=candidate['sha256']==ot.get('sha256') and candidate['path']==norm(ot.get('file'))
            candidate['reusePriorSeamFindings']=candidate['unchangedFromAudit']
        ts.append({'tileId':tile,'coreCount':len(selected),'oldCoreCount':ot.get('coreCount',0),'coreCountDelta':len(selected)-ot.get('coreCount',0),'fullCoreCoverage':len(selected)==16,'adopted4kCandidate':candidate,'selectedSources':selected,'formalAccepted':False})
    result['zones'][z]={'tiles':ts,'selectedCoreCount':sum(t['coreCount'] for t in ts),'oldSelectedCoreCount':sum(t['oldCoreCount'] for t in ts),'adoptedCandidateCount':sum(bool(t['adopted4kCandidate']) for t in ts),'fullCoreCoverageCount':sum(t['fullCoreCoverage'] for t in ts),'partialTileCount':sum(0<t['coreCount']<16 for t in ts),'emptyTileCount':sum(t['coreCount']==0 for t in ts),'formalAcceptedCount':0,'reusedEdgeEvidence':[]}
    full={t['tileId']:t for t in ts if t['adopted4kCandidate'] and t['adopted4kCandidate']['unchangedFromAudit']}
    for edge in old[z].get('pairs',old[z].get('edges',[])):
        ids=edge.get('tiles',[])
        if not ids: ids=[edge.get('from'),edge.get('to')]
        # Retain original evidence data; candidate hash equality is the validity basis.
        result['zones'][z]['reusedEdgeEvidence'].append({'priorEvidence':edge,'candidateReuseSet':list(full),'basis':'Reuse applies only when both listed tile candidate SHA256 values remain unchanged; failed status remains failed.'})
for z,d in result['zones'].items():
    for t in d['tiles']:
        if t['fullCoreCoverage'] and not t['adopted4kCandidate']:
            im=Image.new('RGB',(4096,4096)); tile=t['tileId']
            for s in t['selectedSources']:
                with Image.open(s['path']) as src:
                    assert src.size==(1254,1254)
                    im.paste(src.convert('RGB').crop((115,115,1139,1139)),((s['subcolumn']-1)*1024,(s['subrow']-1)*1024))
            dest=OUT/'native-assemblies'/f'{z}-{tile}-selected-core-hard-join-4096-v02.png';dest.parent.mkdir(exist_ok=True);im.save(dest)
            mismatches=0
            for s in t['selectedSources']:
                x=(s['subcolumn']-1)*1024;y=(s['subrow']-1)*1024
                with Image.open(s['path']) as src: mismatches+=int(im.crop((x,y,x+1024,y+1024)).tobytes()!=src.convert('RGB').crop((115,115,1139,1139)).tobytes())
            assembly={**info(dest),'tileId':tile,'zone':z,'mode':'exact 1024 center-core paste, no resizing/feathering/editing','mismatchingCoreRecrops':mismatches,'adoptedByProduction':False,'status':'diagnostic_pending_visual_review'}
            result['newDiagnosticAssemblies'].append(assembly)
            cropsdir=OUT/'crops'/tile;cropsdir.mkdir(parents=True,exist_ok=True)
            for axis in ['vertical','horizontal']:
                crops=[]
                for boundary in range(1,4):
                    for seg in range(4):
                        k=boundary*1024;a=seg*1024
                        box=(k-256,a,k+256,a+1024) if axis=='vertical' else (a,k-256,a+1024,k+256)
                        crop=im.crop(box);name=f'{axis}-{boundary}-segment-{seg+1}-100pct.png';cp=cropsdir/name;crop.save(cp)
                        crops.append({'path':norm(cp),'tileBox':list(box),'axis':axis,'boundary':boundary,'segment':seg+1})
                # Four exact pixels panels per board; no text overlay.
                for b in range(3):
                    panels=crops[b*4:b*4+4]
                    board=Image.new('RGB',(2048,1024) if axis=='vertical' else (2048,1024))
                    for i,p in enumerate(panels):
                        with Image.open(p['path']) as ci:
                            xy=(i*512,0) if axis=='vertical' else ((i%2)*1024,(i//2)*512)
                            board.paste(ci,xy)
                    bp=cropsdir/f'{axis}-{b+1}-board-100pct.png';board.save(bp)
                    assembly.setdefault('boards',[]).append({'path':norm(bp),'panels':panels})
            # All nine 512px four-core crossing crops in one 1536px unscaled contact sheet.
            board=Image.new('RGB',(1536,1536)); crosses=[]
            for r in range(1,4):
                for c in range(1,4):
                    box=(c*1024-256,r*1024-256,c*1024+256,r*1024+256);board.paste(im.crop(box),((c-1)*512,(r-1)*512));crosses.append(list(box))
            bp=cropsdir/'all-nine-crossings-board-100pct.png';board.save(bp);assembly['crossingBoard']={'path':norm(bp),'tileBoxes':crosses}
            # New full neighboring boundaries.
            rr=int(tile[1:3]);cc=int(tile[5:7]);tmap={tt['tileId']:tt for dd in result['zones'].values() for tt in dd['tiles']}
            for dr,dc,side in [(-1,0,'north'),(0,1,'east'),(1,0,'south'),(0,-1,'west')]:
                nid=f'r{rr+dr:02d}_c{cc+dc:02d}';nt=tmap.get(nid); ca=nt.get('adopted4kCandidate') if nt else None
                if not ca: continue
                with Image.open(ca['path']) as nsrc: ni=nsrc.convert('RGB')
                pans=[]
                for seg in range(4):
                    a=seg*1024
                    if side in ['north','south']:
                        crop=Image.new('RGB',(1024,512))
                        crop.paste(ni.crop((a,3840,a+1024,4096)) if side=='north' else im.crop((a,3840,a+1024,4096)),(0,0))
                        crop.paste(im.crop((a,0,a+1024,256)) if side=='north' else ni.crop((a,0,a+1024,256)),(0,256))
                    else:
                        crop=Image.new('RGB',(512,1024))
                        crop.paste(im.crop((3840,a,4096,a+1024)) if side=='east' else ni.crop((3840,a,4096,a+1024)),(0,0))
                        crop.paste(ni.crop((0,a,256,a+1024)) if side=='east' else im.crop((0,a,256,a+1024)),(256,0))
                    cp=cropsdir/f'neighbor-{side}-{nid}-segment-{seg+1}-100pct.png';crop.save(cp);pans.append(norm(cp))
                board=Image.new('RGB',(2048,1024))
                for i,cp in enumerate(pans):
                    with Image.open(cp) as ci:board.paste(ci,((i%2)*1024,(i//2)*512) if side in ['north','south'] else (i*512,0))
                bp=cropsdir/f'neighbor-{side}-{nid}-board-100pct.png';board.save(bp)
                assembly.setdefault('neighborBoards',[]).append({'path':norm(bp),'side':side,'neighbor':nid,'neighborSource':ca,'panels':pans})
result['inputImageHashCount']=len([p for p in cache if not p.startswith(norm(OUT))])
result['finishedCaptureAtUtc']=datetime.now(timezone.utc).isoformat()
save(OUT/'source-delta.json',result)
print(json.dumps({z:{k:v for k,v in d.items() if k not in ['tiles','reusedEdgeEvidence']} for z,d in result['zones'].items()},ensure_ascii=False))
print('changedTiles',[(z,t['tileId'],t['oldCoreCount'],t['coreCount'],sum(s['change']!='unchanged' for s in t['selectedSources'])) for z,d in result['zones'].items() for t in d['tiles'] if t['coreCountDelta'] or any(s['change']!='unchanged' for s in t['selectedSources'])])
print('candidateChanges',[(z,t['tileId']) for z,d in result['zones'].items() for t in d['tiles'] if t['adopted4kCandidate'] and not t['adopted4kCandidate']['unchangedFromAudit']])
print('newAssemblies',[(a['tileId'],a['path']) for a in result['newDiagnosticAssemblies']])
