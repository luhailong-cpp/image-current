"""Tile-local provenance and native conditioning for resumed builtin artwork."""
from pathlib import Path
import sys, json, hashlib, shutil
from datetime import datetime, timezone
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import tile_native_workflow as wf

T=Path(__file__).resolve().parent
TILE=T.name
REFS=[r['path'] for r in wf.read(T/'coordinate-plan.json')['references']]
COMMON='''Use case: stylized-concept. Edit reference image 1 into one finished native 1254 x 1254 pixel game-world patch, at its EXACT footprint and fixed camera. Output only the same 1254-square. Image 1 is a target guide: its crisp outer strips are exact native neighboring artwork; all remaining blurred area defines composition and must become NEW sharp native detail. Preserve crisp strip contours, materials and color, especially across eventual core cuts at 115px and 1139px. Connect forms naturally across the guide boundary at 230px/1024px with no rectangular line or blurred guide pixels. Do not repeat the neighbor, reframe, zoom, rescale, or create a miniature whole map.
Reference 2 is authoritative full-map LAYOUT ONLY. Reference 3 is independent daylight/material STYLE, not a coordinate crop. Reference 4 is approved polished Daoist Q painterly STYLE ONLY; never copy UI, text, characters, or night lighting. Fixed orthographic/isometric game camera; bright clear daylight; full rounded friendly forms, broad painterly surfaces and sharp gentle contours. Match the supplied neighbor texture density and palette, no photographic grain. Preserve existing coastal geography, paths, buildings, silhouettes and object positions. No invented props, people, animals, boats, buildings, labels, text, watermark, border or grid. Render only existing material and form at native resolution.
'''
ROLES={'1':'Exact target footprint with latest available native neighbor overlap','2':'Full map layout only','3':'Independent daylight and material style','4':'Approved Daoist painterly style only'}
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def prepare(pid,version,detail):
    plan=wf.read(T/'coordinate-plan.json');target=wf.patch(plan,pid)
    sources=[]
    for nt in (TILE, 'r09_c08','r09_c10','r08_c09','r10_c09'):
        P=T.parent/nt
        sp=P/'selected-patches.json'
        if not sp.exists():continue
        pp=wf.plan_path(nt)
        np=wf.read(pp);sel=wf.read(sp)
        for sid,rel in sel['patches'].items():
            if nt==TILE and sid==pid:continue
            sb=wf.patch(np,sid)['globalBox'];tb=target['globalBox']
            if max(sb[0],tb[0])<min(sb[2],tb[2]) and max(sb[1],tb[1])<min(sb[3],tb[3]):
                cardinal=(sb[0]==tb[0] or sb[1]==tb[1])
                sources.append((cardinal,nt,sid,rel))
    sources.sort(key=lambda a:(a[0], a[2][2]==pid[2], a[2]))
    conditioned=wf.condition(TILE,pid,[f'{nt}:{sid}:{rel}' for _,nt,sid,rel in sources])
    refs=[conditioned['file']]+REFS
    prompt=COMMON+detail+'\nNative 1254x1254, 115px halo, central exact 1024px core. Preserve all submitted geometry and supplied seam endpoints.'
    stem=f'{pid}-{version}'
    pp=T/f'{stem}.prompt.txt';rp=T/f'{stem}.request.json'
    if pp.exists() or rp.exists():raise FileExistsError(stem)
    pp.write_text(prompt,encoding='utf-8')
    req={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False,'route':'builtin','tool':'image_gen__imagegen','submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None,'createdAt':now(),'referenceRoles':ROLES,'referenceEvidence':[{'path':p,'sha256':sha(p),'role':ROLES[str(i)]} for i,p in enumerate(refs,1)]}
    write(rp,req)
    return {'request':str(rp),'target':conditioned['file'],'nativeSourceCount':len(sources),'promptSha256':sha(pp)}
def receipt(pid,version,source,raw_response):
    im=Image.open(source);im.load()
    raw=T/'raw'/f'{pid}-{version}-builtin.png';raw.parent.mkdir(exist_ok=True)
    if raw.exists():raise FileExistsError(raw)
    shutil.copy2(source,raw)
    data={'receivedAt':now(),'sourcePath':str(raw),'builtinSourcePath':source,'toolResponse':raw_response,'tool':'image_gen__imagegen','route':'builtin','actualModel':None,'actualQuality':None,'nativeDimensions':list(im.size),'sha256':sha(raw)}
    write(T/f'{pid}-{version}.receipt.json',data)
    return data
def progress():
    sel=wf.read(T/'selected-patches.json');items=[]
    for pid,rel in sel['patches'].items():
        p=T/rel;g=wf.read(p.with_suffix('.png.generation.json'))
        items.append({'patch':pid,'file':str(p),'sha256':sha(p),'nativeSize':g['nativeDimensions'],'generationRecord':str(p.with_suffix('.png.generation.json')),'corePixels':1024**2})
    p=wf.read(T/'progress.json')
    p.update(status='resumed_native_production_20261012',generatedNativeCount=len(list((T/'native').glob('p*-v*.png'))),selectedPatchCount=len(items),usableNativeCount=len(items),exactCoreCoverage=len(items)*1024**2,coverageFraction=len(items)/16,selectedSources=items,remainingPositions=[f'p{r}{c}' for r in range(1,5) for c in range(1,5) if f'p{r}{c}' not in sel['patches']],updatedAt=now(),nextStep='Continue missing patches from south to north, then inspect all internal and available external joins',resumeAuthority='D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json')
    write(T/'progress.json',p)
    return {'selectedCount':len(items),'coverageFraction':len(items)/16}
if __name__=='__main__':
    op=sys.argv[1]
    if op=='prepare':result=prepare(sys.argv[2],sys.argv[3],Path(sys.argv[4]).read_text(encoding='utf-8-sig'))
    elif op=='receipt':result=receipt(sys.argv[2],sys.argv[3],sys.argv[4],json.loads(Path(sys.argv[5]).read_text(encoding='utf-8-sig')))
    elif op=='progress':result=progress()
    print(json.dumps(result,ensure_ascii=False))
