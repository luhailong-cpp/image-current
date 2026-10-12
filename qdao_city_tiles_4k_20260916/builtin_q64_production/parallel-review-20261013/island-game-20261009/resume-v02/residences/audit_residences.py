import json, hashlib, re
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

ROOT = Path('D:/work/image')
BASE = ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production'
OUT = BASE/'parallel-review-20261013/island-game-20261009/resume-v02/residences'
OUT.mkdir(parents=True, exist_ok=True)
def now(): return datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def resolve(p):
    p=Path(p)
    return p if p.is_absolute() else ROOT/p
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def info(p):
    p=Path(p); d={'path':p.as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
    if p.suffix.lower()=='.png':
        with Image.open(p) as im: d.update(dimensions=list(im.size),mode=im.mode)
    return d
def save(name,j): (OUT/name).write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')

started=now()
split=read(ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json')
batches=[b for b in split['batches'] if b['key'] in ['island-west-residences','island-east-residences']]
snapshot={'createdAtUtc':started,'scope':'read-only current residence production delta; original files unchanged','rules':info(ROOT/'AGENTS.md'),'split':info(ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json'),'batches':[]}
native_by_stem={}
for batch in batches:
    folder=resolve(batch['outputDirectory'])
    files=sorted(p for p in folder.rglob('*') if p.is_file())
    listing=[{'relativePath':p.relative_to(folder).as_posix(),'bytes':p.stat().st_size,'mtimeUtc':datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat()} for p in files]
    focused=[p for p in files if p.suffix=='.json' and (p.parent.name in ['native','qa','reviews','reviews-input'] or 'selections' in p.parts or p.name.startswith('batch-status'))]
    evidence=[]; docs={}
    for p in focused:
        j=read(p); docs[p]=j; evidence.append({'file':info(p),'content':j})
    natives=[]
    for p in files:
        if p.parent.name=='native' and p.suffix=='.png':
            meta=docs.get(Path(str(p)+'.generation.json'),{})
            id=p.stem; reviews=[{'file':info(q),'content':j} for q,j in docs.items() if q.parent.name in ['qa','reviews','reviews-input'] and (j.get('id')==id or j.get('stem')==id)]
            match=re.match(r'(r\d+_c\d+)_[ps](\d+)_(\d+)',id)
            item={'id':id,'tileId':match[1],'subrow':int(match[2]),'subcolumn':int(match[3]),'file':info(p),'generation':meta,'reviews':reviews,'selected':False}
            item['generationHashMatches']=meta.get('sha256')==item['file']['sha256']
            natives.append(item); native_by_stem[id]=item
    tiles=[]
    for tile in batch['tiles']:
        sels=[(p,j) for p,j in docs.items() if 'selections' in p.parts and j.get('tileId')==tile]
        sels.sort(key=lambda x:(x[1].get('createdAtUtc',''),x[0].name))
        matrix=[[None]*4 for _ in range(4)]; selection=None
        if sels:
            p,j=sels[-1]; selection={'file':info(p),'content':j}
            for coord,val in j.get('selected',{}).items():
                m=re.match(r'r\d+_c\d+_[ps](\d+)_(\d+)',coord)
                f=resolve(val['file']); item={'id':val['id'],'file':info(f),'selectionSha256':val['sha256'],'hashMatchesSelection':sha(f)==val['sha256']}
                matrix[int(m[1])-1][int(m[2])-1]=item
                if val['id'] in native_by_stem: native_by_stem[val['id']]['selected']=True
        count=sum(c is not None for row in matrix for c in row)
        tiles.append({'tileId':tile,'currentSelection':selection,'selectedCoreMatrix':matrix,'selectedCoreCount':count,'missingCoreCount':16-count,'full4096Candidate':None,'formalAccepted':False,'availableNativeIds':[n['id'] for n in natives if n['tileId']==tile]})
    snapshot['batches'].append({'key':batch['key'],'allocation':batch,'directory':folder.as_posix(),'listing':listing,'metadataEvidence':evidence,'tiles':tiles,'native':natives})

# Only eight directly adjacent existing adopted images. Prior inventory supplies pinned paths;
# current source hashes and selection records are verified without replaying old interior audits.
nwpath=BASE/'island-game-20261009/northwest/current-adopted-20261012.json'
nw=read(nwpath)
neinv=read(BASE/'parallel-review-20261013/island-game-20261009/root-audit-v01/inventory.json')
neighbors={}
for t in nw['tiles']:
    if t['tileId'] in ['r03_c02','r03_c03','r03_c04']:
        n=info(resolve(t['image']['path'])); n.update(expectedSha256=t['image']['sha256'],selectionRecord=info(nwpath)); n['hashMatches']=n['sha256']==n['expectedSha256']; neighbors[t['tileId']]=n
for t in neinv['tiles']:
    if t['tileId'] in ['r03_c10','r03_c11','r03_c12','r01_c13','r02_c13']:
        n=info(resolve(t['file'])); n.update(expectedSha256=t['sha256'],selectionRecord=info(resolve(t['selectionFile']))); n['hashMatches']=n['sha256']==n['expectedSha256']; neighbors[t['tileId']]=n
snapshot['neighborSources']=neighbors
seams=[]
def make_seam(stem,neighbor,direction):
    n=native_by_stem[stem]; src=resolve(n['file']['path']); dst=resolve(neighbors[neighbor]['path'])
    with Image.open(src) as a,Image.open(dst) as b:
        a=a.convert('RGB'); b=b.convert('RGB'); sr=n['subrow']; sc=n['subcolumn']
        if direction=='south':
            boxes=[[115,883,1139,1139],[(sc-1)*1024,0,sc*1024,256]]
            out=Image.new('RGB',(1024,512)); out.paste(a.crop(boxes[0]),(0,0));out.paste(b.crop(boxes[1]),(0,256))
            tile_r=int(n['tileId'][1:3]); tile_c=int(n['tileId'][5:7]); x=(tile_c-1)*4096+(sc-1)*1024; y=tile_r*4096
            world=[x,y-256,x+1024,y+256]
        else:
            boxes=[[883,115,1139,1139],[0,(sr-1)*1024,256,sr*1024]]
            out=Image.new('RGB',(512,1024));out.paste(a.crop(boxes[0]),(0,0));out.paste(b.crop(boxes[1]),(256,0))
            tile_r=int(n['tileId'][1:3]); tile_c=int(n['tileId'][5:7]); x=tile_c*4096;y=(tile_r-1)*4096+(sr-1)*1024
            world=[x-256,y,x+256,y+1024]
        file=OUT/f'{stem}-{direction}-{neighbor}-100pct.png';out.save(file)
        seams.append({'nativeId':stem,'selected':n['selected'],'neighbor':neighbor,'direction':direction,'worldBox':world,'sourceCropBoxes':boxes,'sources':[n['file'],neighbors[neighbor]],'output':info(file),'operation':'integer unscaled core-edge hard join; 256 px each side; diagnostic only','visualReviewed':False,'status':'pending_visual_review'})
for stem,neighbor in [('r02_c02_s04_01_a01','r03_c02'),('r02_c10_p04_04_v02','r03_c10'),('r02_c11_p04_04_v02','r03_c11'),('r02_c12_p04_04_v03','r03_c12')]:
    if stem in native_by_stem: make_seam(stem,neighbor,'south')
if 'r02_c12_p04_04_v03' in native_by_stem: make_seam('r02_c12_p04_04_v03','r02_c13','east')
snapshot['seams']=seams
snapshot['capturedAtUtc']=now()
save('snapshot.json',snapshot)
print(json.dumps({'snapshot':str(OUT/'snapshot.json'),'tiles':[{k:t[k] for k in ['tileId','selectedCoreCount','availableNativeIds']} for b in snapshot['batches'] for t in b['tiles']],'nativeCount':len(native_by_stem),'seams':[s['output']['path'] for s in seams]},ensure_ascii=False,indent=2))
