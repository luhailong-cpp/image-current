"""Exclusive r08 c01..07 worker: coordinate guides, records, local selections only."""
from pathlib import Path
import sys,json,shutil
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import production as p
INDEX=ROOT/'qa/expansion-north-worker-map.json'
def state():
    return p.load(INDEX) if INDEX.exists() else {**{f'r08_c{c:02}':[[None]*4 for _ in range(4)] for c in range(1,8)},'status':'north_native_generation','formalAccepted':False,'generationCount':0,'qa':{},'candidateArtifacts':{}}
def save(d):
    d['updatedAtUtc']=p.now();p.dump(INDEX,d)
def inter(a,b):
    z=[max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3])]
    return z if z[0]<z[2] and z[1]<z[3] else None
def prepare(c,sr,sc,attempt=1):
    assert 1<=c<=7 and 1<=sr<=4 and 1<=sc<=4
    co=p.coords(8,c,sr,sc);tile=co['tile'];stem=f'{tile}_s{sr:02}_{sc:02}_v{attempt:02}'
    request=ROOT/'prompts'/f'{stem}.request.json'
    assert not request.exists(), 'Prepared inputs immutable; inspect existing request before retry'
    layout=ROOT/'guides'/f'{stem}.layout-only.png'
    with Image.open(p.REFS[0][0]) as im: im.transform((1254,1254),Image.Transform.EXTENT,co['overviewFloatBox'],Image.Resampling.BICUBIC).save(layout)
    p.dump(str(layout)+'.derivation.json',{'file':str(layout),'sha256':p.hashfile(layout),'operation':'Layout-only overview extent; no final contribution','source':p.metadata(*p.REFS[0]),'coordinates':co})
    canvas=Image.open(layout).convert('RGB');sources=[p.metadata(layout,'blurry layout-only remainder')];d=state();main=p.load(ROOT/'current-native-map.json');box=co['nativeGlobalBox'];neighbors=[]
    # Closest vertical native anchor first. Search all selected neighbors for 230px overlap.
    maps={**{k:v for k,v in main.items() if k.startswith('r') and isinstance(v,list)},**{k:v for k,v in d.items() if k.startswith('r08_')}}
    for key,rows in maps.items():
      for row in rows:
       for n in row:
        if not isinstance(n,str):continue
        path=ROOT/'native'/f'{n}.png';rec=p.load(str(path)+'.generation.json');nb=rec['coordinates']['nativeGlobalBox'];z=inter(box,nb)
        if z and (z[2]-z[0])*(z[3]-z[1])>=230*230:neighbors.append((n,nb,z))
    neighbors.sort(key=lambda n:(0 if n[1][1]>box[1] and n[1][0]==box[0] else 1,n[0]))
    for n,nb,z in neighbors:
      path=ROOT/'native'/f'{n}.png';crop=[z[0]-nb[0],z[1]-nb[1],z[2]-nb[0],z[3]-nb[1]];dest=[z[0]-box[0],z[1]-box[1]]
      canvas.paste(Image.open(path).crop(crop),dest);sources.append({**p.metadata(path,'same-coordinate selected native neighbor'),'sourceCrop':crop,'destinationTopLeft':dest})
    # Exported 4K is exact boundary priority over the older native raw patch.
    for key,art in main.get('candidateArtifacts',{}).items():
      rnum,cnum=map(int,[key[1:3],key[5:7]]);fb=[(cnum-1)*4096,(rnum-1)*4096,cnum*4096,rnum*4096];z=inter(box,fb)
      if not z:continue
      path=Path(art['path']);ar=p.load(art['record']);expected=art.get('sha256') or ar.get('sha256');assert expected and p.hashfile(path)==expected;crop=[z[0]-fb[0],z[1]-fb[1],z[2]-fb[0],z[3]-fb[1]];dest=[z[0]-box[0],z[1]-box[1]]
      canvas.paste(Image.open(path).crop(crop),dest);sources.append({**p.metadata(path,'official current native 4K border; highest priority'),'sourceCrop':crop,'destinationTopLeft':dest})
    guide=ROOT/'guides'/f'{stem}.native-overlap-guide.png';canvas.save(guide)
    p.dump(str(guide)+'.derivation.json',{'file':str(guide),'sha256':p.hashfile(guide),'operation':'Same-coordinate native crop/paste over layout-only overview; no native resampling or painting','sources':sources,'coordinates':co})
    refs=[p.metadata(guide,'edit target; existing sharp native overlaps fixed, blurry remainder layout-only')]+[p.metadata(*r) for r in p.REFS]
    # Keep only the target and three mandatory references; unrelated adjacent scene extent can overpower the crop.
    prompt=f'''Use case: precise-object-edit. Output exactly 1254 by 1254 pixels, opaque native square.
Image 1 is the fixed-coordinate guide for Eight Immortals Island tile {tile}, native cell row {sr}, column {sc}, global box {box}. Render the blurry layout-only region into crisp full-native-detail painted game art, while preserving every existing sharp native overlap at its exact pixel position and geometry. Continue the same objects smoothly through the transitions; no change of scale, angle, framing or object placement. The sole composition is the corresponding tiny crop of Image 2, not the full map. Do not copy the full-map scene into this crop. Preserve roof ridge locations, tile directions and sizes, bamboo/trunk placement, ground geometry and other major shapes seen in the guide. Do not invent buildings, characters, props, ornaments, flowers or roads. Image 3 provides independent material close-up style only; it is not a coordinate crop. Image 4 provides approved Daoist Q painterly style only, no UI or night-scene transfer. Image 5, if supplied, is neighboring native style/geometry context; the sharp parts in Image 1 remain the authoritative exact boundary. Warm daylight, clear blue glazed roofs with gold/red-orange trim, natural stone and rich green bamboo as locally present. Fine clean native brush facets, coherent highlights and shading. No blurry strip, soft seam, vignette, watermark, border or text. Keep all sharp boundary geometry immobile, and generate genuine native detail only in the missing region.'''
    (ROOT/'prompts'/f'{stem}.prompt.txt').write_text(prompt,encoding='utf-8');p.dump(ROOT/'prompts'/f'{stem}.coordinates.json',co)
    p.dump(request,{'tool':'image_gen.imagegen','references':refs,'coordinates':co,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None})
    d['currentPatch']=stem;d['nextStep']='Inspect guide; generate built-in native; inspect before selection';save(d)
    print(json.dumps({'stem':stem,'guide':str(guide),'prompt':prompt,'refs':[x['path'] for x in refs]}))
def ingest(stem,source):
    p.update=lambda **kw:None
    p.ingest(stem,source)
    d=state();d['generationCount']+=1;d['lastGenerated']=stem;save(d)
def select(stem,note):
    co=p.load(ROOT/'prompts'/f'{stem}.coordinates.json');assert co['tile'].startswith('r08_')
    d=state();d[co['tile']][co['subrow']-1][co['subcolumn']-1]=stem;d['qa'][stem]={'status':'native visually checked candidate; assembled seams pending','note':note,'reviewedAtUtc':p.now()};d['selectedCoreCount']=sum(bool(n) for c in range(1,8) for row in d[f'r08_c{c:02}'] for n in row);save(d)
    print(json.dumps({'selected':stem,'selectedCoreCount':d['selectedCoreCount']}))
if __name__=='__main__':
    cmd=sys.argv[1]
    if cmd=='prepare':prepare(*map(int,sys.argv[2:]))
    elif cmd=='ingest':ingest(*sys.argv[2:])
    elif cmd=='select':select(*sys.argv[2:])
