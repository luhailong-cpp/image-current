from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib,shutil
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import tile_native_workflow as wf
T=Path(__file__).resolve().parent; TILE=T.name; Z=T.parent
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
COMMON='''Use case: stylized-concept. Edit input image 1 into exactly one finished native 1254 x 1254 RGB pixel game map patch at the exact supplied camera and footprint. Output ONLY this same 1254-square patch. Input 1 is the edit TARGET. Its sharp outer frame, where present, contains exact neighboring selected core pixels. These frame pixels are fixed seam constraints. The remaining blurred center defines positions and silhouettes ONLY and must become NEW sharp painterly native detail. Do not preserve or imitate blur. Do not move any object, enlarge/reframe the scene, or substitute a whole-map thumbnail. The central 1024 core extends from x,y 115 through 1138 inclusive. Keep contours, material grain, shadows and colors connected at the exact core cuts x/y115 and1139. Do not create rectangular color/texture edges, seams or duplicated outlines.
Input 2 is authoritative full-map LAYOUT ONLY. Input 3 is independent daylight/material STYLE only, not a coordinate crop. Input 4 is the approved polished Daoist Q painterly STYLE only. Never copy its UI, lettering, characters or night lighting. Use the same fixed orthographic/isometric game camera, clear bright daylight, rounded friendly shapes, broad painterly material strokes and crisp gentle contours. Match supplied native neighbor density and color. Preserve the existing stone grout coordinates, lantern/post/body silhouettes, fish ornament, foliage, building outlines and path geography where visible in target. No new props, buildings, people, animals, boats, NPCs, text, signs, labels, watermark, border or grid. Render the existing target forms only, with sharp real native detail.
'''
ROLES={'1':'Exact target footprint, with unscaled actual selected CORE pixels on outer115 halo only; blurred layout inside needs native rendering','2':'Authoritative full map layout only','3':'Independent daylight material style only','4':'Approved Daoist Q painterly style only'}
def prepare(pid,version,detail=''):
    plan=read(T/'coordinate-plan.json');target=wf.patch(plan,pid);tb=target['globalBox']; image=Image.open(target['file']).convert('RGB'); sources=[]
    r,c=wf.tile_indices(TILE)
    for rr in range(r-1,r+2):
      for cc in range(c-1,c+2):
        nt=f'r{rr:02d}_c{cc:02d}'; sp=Z/nt/'selected-patches.json'
        if not sp.exists():continue
        np=read(wf.plan_path(nt)); sel=read(sp); sh=sha(sp)
        for sid,rel in sel['patches'].items():
            if nt==TILE and sid==pid:continue
            sc=wf.patch(np,sid);sb=sc['coreBox'];over=[max(sb[0],tb[0]),max(sb[1],tb[1]),min(sb[2],tb[2]),min(sb[3],tb[3])]
            if over[0]>=over[2] or over[1]>=over[3]:continue
            p=Z/nt/rel; n=Image.open(p);n.load();assert n.size==(1254,1254) and n.mode=='RGB'
            crop=[115+over[0]-sb[0],115+over[1]-sb[1],115+over[2]-sb[0],115+over[3]-sb[1]];at=[over[0]-tb[0],over[1]-tb[1]]
            image.paste(n.crop(crop),tuple(at))
            assert at[0]+crop[2]-crop[0]<=115 or at[0]>=1139 or at[1]+crop[3]-crop[1]<=115 or at[1]>=1139,'Actual neighbor core must not replace target own core'
            rp=Path(str(p)+('.generation.json' if p.parent.name=='native' else '.derivation.json'))
            sources.append(dict(sourceTile=nt,sourcePatch=sid,file=str(p),sha256=sha(p),coreBox=sb,globalOverlapBox=over,crop=crop,pasteAt=at,operation='unscaled actual CORE pixel copy, never use unfinished neighbor halo',record=str(rp),recordSha256=sha(rp),selection=str(sp),selectionSha256=sh))
        assert sha(sp)==sh,'Neighbor selection changed while conditioning'
    stem=f'{pid}-{version}';guide=T/'layout-only'/f'{stem}-actual-core-conditioned.png';assert not guide.exists();image.save(guide)
    write(str(guide)+'.derivation.json',dict(file=str(guide),sha256=sha(guide),dimensions=[1254,1254],classification='input guide only, never final art',targetGlobalBox=tb,coreBox=target['coreBox'],baseLayout=target['file'],baseLayoutSha256=sha(target['file']),nativeCoreSources=sources,createdAt=now()))
    refs=[str(guide)]+[x['path'] for x in plan['references']]
    prompt=COMMON+detail+'\nNative 1254x1254. Keep exact supplied geometry and supplied seam endpoints; render every blurred existing surface at real native detail.'
    pp=T/f'{stem}.prompt.txt';rp=T/f'{stem}.request.json';assert not pp.exists() and not rp.exists();pp.write_text(prompt,encoding='utf-8')
    req=dict(prompt=prompt,referenced_image_paths=refs,transparent_background=False,route='builtin',tool='image_gen__imagegen',submittedModel=None,submittedQuality=None,actualModel=None,actualQuality=None,createdAt=now(),referenceRoles=ROLES,referenceEvidence=[dict(path=p,sha256=sha(p),role=ROLES[str(i)]) for i,p in enumerate(refs,1)])
    write(rp,req)
    return dict(request=str(rp),target=str(guide),nativeSourceCount=len(sources),promptSha256=sha(pp))
def receipt(pid,version,source,response):
    im=Image.open(source);im.load(); raw=T/'raw'/f'{pid}-{version}-builtin.png';raw.parent.mkdir(exist_ok=True);assert not raw.exists();shutil.copy2(source,raw)
    d=dict(receivedAt=now(),sourcePath=str(raw),builtinSourcePath=source,toolResponse=response,tool='image_gen__imagegen',route='builtin',actualModel=None,actualQuality=None,nativeDimensions=list(im.size),sha256=sha(raw));write(T/f'{pid}-{version}.receipt.json',d);return d
def progress():
    sel=read(T/'selected-patches.json');items=[]
    for pid,rel in sel['patches'].items():
        p=T/rel;g=read(str(p)+'.generation.json');items.append(dict(patch=pid,file=str(p),sha256=sha(p),nativeSize=g['nativeDimensions'],generationRecord=str(p)+'.generation.json',corePixels=1024**2))
    p=dict(tile=TILE,status='native_production_20261012',updatedAt=now(),generatedNativeCount=len(list((T/'native').glob('*.png.generation.json'))),selectedPatchCount=len(items),usableNativeCount=len(items),exactCoreCoverage=len(items)*1024**2,coverageFraction=len(items)/16,selectedSources=items,remainingPositions=[f'p{r}{c}' for r in range(1,5) for c in range(1,5) if f'p{r}{c}' not in sel['patches']],complete4kCount=0,internalReady4kCount=0,formalAcceptedCount=0,internalReady=False,formalAccepted=False,actualModel=None,actualQuality=None,resumeAuthority='D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json',nextStep='Continue missing patches from south to north then review all33 internal and all available external joints')
    write(T/'progress.json',p);return dict(selectedCount=len(items),coverageFraction=len(items)/16)
if __name__=='__main__':
    op=sys.argv[1]
    if op=='prepare':d=prepare(sys.argv[2],sys.argv[3],sys.argv[4] if len(sys.argv)>4 else '')
    elif op=='receipt':
        x=receipt(sys.argv[2],sys.argv[3],sys.argv[4],read(sys.argv[5]));d={k:x[k] for k in ['sourcePath','nativeDimensions','sha256','actualModel','actualQuality']}
    elif op=='progress':d=progress()
    print(json.dumps(d,ensure_ascii=False))
