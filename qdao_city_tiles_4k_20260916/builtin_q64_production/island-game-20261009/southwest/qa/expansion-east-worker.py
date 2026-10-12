"""Exclusive eastern native map worker; mechanical guides and records only."""
import sys,json,shutil,argparse
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
import production as p
INDEX=ROOT/'qa'/'expansion-east-worker-map.json'
def state():
    return p.load(INDEX) if INDEX.exists() else {'owner':'finish_c04/east','assignedTiles':[f'r{r:02}_c{c:02}' for r in range(9,15) for c in range(5,8)],'generationCount':0,'status':'in_progress','formalAccepted':False,'qa':{},'candidateArtifacts':{}}
def save(d):
    d['updatedAtUtc']=p.now();p.dump(INDEX,d)
def box_intersection(a,b):
    v=[max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3])]
    return v if v[2]>v[0] and v[3]>v[1] else None
def prepare(r,c,sr,sc,attempt=1):
    d=state();tile=f'r{r:02}_c{c:02}';assert tile in d['assignedTiles'];d.setdefault(tile,[[None]*4 for _ in range(4)])
    co=p.coords(r,c,sr,sc);stem=f'{tile}_s{sr:02}_{sc:02}_v{attempt:02}';reqpath=ROOT/'prompts'/f'{stem}.request.json'
    assert not reqpath.exists(),'Existing request; reuse immutable inputs rather than overwrite'
    layout=ROOT/'guides'/f'{stem}.layout-only.png'
    with Image.open(p.REFS[0][0]) as im:im.transform((1254,1254),Image.Transform.EXTENT,co['overviewFloatBox'],Image.Resampling.BICUBIC).save(layout)
    p.dump(str(layout)+'.derivation.json',{'operation':'Layout-only overview coordinate EXTENT; not final native contribution','source':p.metadata(*p.REFS[0]),'coordinates':co,'sha256':p.hashfile(layout)})
    canvas=Image.open(layout).convert('RGB');sources=[p.metadata(layout,'layout-only base')];box=co['nativeGlobalBox'];maps=[p.load(ROOT/'current-native-map.json'),d]
    # Read north/central neighbors if they have produced a coordinate that touches this patch.
    for n in ['expansion-north-worker-map.json','expansion-central-worker-map.json']:
        q=ROOT/'qa'/n
        if q.exists():maps.append(p.load(q))
    selected={}
    artifacts={}
    for m in maps:
        selected.update({k:v for k,v in m.items() if k.startswith('r') and isinstance(v,list) and len(v)==4})
        artifacts.update(m.get('candidateArtifacts',{}))
    native_neighbors=[]
    for nt,grid in selected.items():
        for row in grid:
            for ns in row:
                if not ns or ns.startswith(f'{tile}_s{sr:02}_{sc:02}_'):continue
                np=ROOT/'native'/f'{ns}.png';rec=p.load(str(np)+'.generation.json');nb=rec['coordinates']['nativeGlobalBox'];ib=box_intersection(box,nb)
                if not ib:continue
                crop=[ib[0]-nb[0],ib[1]-nb[1],ib[2]-nb[0],ib[3]-nb[1]];dest=[ib[0]-box[0],ib[1]-box[1]]
                canvas.paste(Image.open(np).crop(crop),dest);sources.append({**p.metadata(np,'same-coordinate adjacent native overlap'),'sourceCrop':crop,'destinationTopLeft':dest,'nativeGlobalBox':nb});native_neighbors.append(ns)
    for nt,art in artifacts.items():
        nr,nc=map(int,[nt[1:3],nt[5:7]]);nb=[(nc-1)*4096,(nr-1)*4096,nc*4096,nr*4096];ib=box_intersection(box,nb)
        if not ib:continue
        ap=Path(art['path']);crop=[ib[0]-nb[0],ib[1]-nb[1],ib[2]-nb[0],ib[3]-nb[1]];dest=[ib[0]-box[0],ib[1]-box[1]]
        canvas.paste(Image.open(ap).crop(crop),dest);sources.append({**p.metadata(ap,'latest complete native candidate border; priority over raw core'),'sourceCrop':crop,'destinationTopLeft':dest,'globalBox':nb,'record':art.get('record',art.get('sourceReport'))})
    guide=ROOT/'guides'/f'{stem}.native-overlap-guide.png';canvas.save(guide)
    p.dump(str(guide)+'.derivation.json',{'operation':'Same-coordinate native crop/paste over layout-only overview; no art resampling or mixing','sources':sources,'coordinates':co,'sha256':p.hashfile(guide)})
    refs=[p.metadata(guide,'edit target: exact native overlap constraints, blurry remainder is layout-only')]+[p.metadata(*ref) for ref in p.REFS]
    req={'tool':'image_gen.imagegen','references':refs,'coordinates':co,'nativeNeighbors':native_neighbors,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None}
    p.dump(reqpath,req);p.dump(ROOT/'prompts'/f'{stem}.coordinates.json',co);d['currentStem']=stem;d['status']='guide_ready';save(d)
    print(json.dumps({'stem':stem,'guide':str(guide),'refs':[x['path'] for x in refs],'coordinates':co,'nativeNeighbors':native_neighbors}))
def ingest(stem,source):
    dst=ROOT/'native'/f'{stem}.png';assert not dst.exists();shutil.copy2(source,dst)
    with Image.open(dst) as im: size=list(im.size);fmt=im.format
    req=p.load(ROOT/'prompts'/f'{stem}.request.json')
    rec={'file':str(dst),'sha256':p.hashfile(dst),'generatedAt':p.now(),'width':size[0],'height':size[1],'format':fmt,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':p.CONFIG,'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host exposes neither selectors nor returned actual model/quality.','prompt':str(ROOT/'prompts'/f'{stem}.prompt.txt'),'promptSha256':p.hashfile(ROOT/'prompts'/f'{stem}.prompt.txt'),'references':req['references'],'sourceToolPath':source,'evidence':[{'path':str(ROOT/'receipts'/f'{stem}.tool.json'),'type':'tool receipt'}],'coordinates':req['coordinates'],'status':'awaiting_visual_QA','nativeSizeMatchesPlan':size==[1254,1254]}
    p.dump(str(dst)+'.generation.json',rec);d=state();d['generationCount']+=1;d['lastGenerated']=stem;d['status']='native_awaiting_QA';save(d)
    print(json.dumps({'file':str(dst),'dimensions':size,'sha256':rec['sha256']}))
def select(stem,note):
    co=p.load(ROOT/'prompts'/f'{stem}.coordinates.json');d=state();tile=co['tile'];assert tile in d['assignedTiles'];d.setdefault(tile,[[None]*4 for _ in range(4)])[co['subrow']-1][co['subcolumn']-1]=stem
    d['qa'][stem]={'status':'selected_native_candidate','note':note,'reviewedAtUtc':p.now(),'formalAccepted':False};d['status']='in_progress';save(d)
def prompt(stem,note):
    text='Use case: precise-object-edit / native scene extension.\nCreate ONE finished native 1254x1254 square map patch using image 1 as exact spatial target. Sharp overlap strips in image 1 are existing finished neighboring art: preserve their shapes, scale, geometry, material, colors, daylight and joint positions; continue them seamlessly into the blurry region. Blurry regions are position guides only and must become crisp native painterly detail. Never scale or move the existing geometry.\nImage 2 is the sole full-map layout reference; image 3 is independent material/detail style only; image 4 is approved Daoist Q painterly style only. Do not transfer objects, text, UI or night lighting from style images.\n'+note+'\nKeep the exact crop, camera angle, layout and object count of image 1. Match pale gray/blue-gray paving, warm golden wood/metal where present, clean blue ceramic, and ivory stone where indicated. Soft warm daylight, crisp rounded Q painterly brush textures, no photographic noise. No invented people, animals, buildings, plants, flowers, props, ornaments, letters, labels, grid, watermark or UI. Do not invent festive objects beyond the guide. Return only the native 1254x1254 artwork.'
    (ROOT/'prompts'/f'{stem}.prompt.txt').write_text(text,encoding='utf-8');print(json.dumps({'stem':stem,'prompt':text,'refs':[x['path'] for x in p.load(ROOT/'prompts'/f'{stem}.request.json')['references']]}))
if __name__=='__main__':
    cmd=sys.argv[1]
    if cmd=='prepare':prepare(*map(int,sys.argv[2:]))
    elif cmd=='ingest':ingest(*sys.argv[2:])
    elif cmd=='select':select(*sys.argv[2:])
    elif cmd=='prompt':prompt(*sys.argv[2:])
