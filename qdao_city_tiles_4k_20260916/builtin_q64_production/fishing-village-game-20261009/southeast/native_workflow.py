"""Mechanical file/coordinate provenance and overlap guide operations only."""
from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import hashlib, json, shutil, sys

ZONE=Path(__file__).resolve().parent
TILE=ZONE/'r10_c09'
PLAN=json.loads((ZONE/'coordinate-plan.json').read_text(encoding='utf-8'))
CONFIG=ZONE.parents[3]/'config'/'image-generation.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def patch(pid): return next(p for p in PLAN['patches'] if p['id']==pid)
mode=sys.argv[1]
if mode=='ingest':
    pid,version,src=sys.argv[2:5]
    stem=f'{pid}-{version}'
    dest=TILE/'native'/f'{stem}.png'
    dest.parent.mkdir(exist_ok=True)
    shutil.copy2(src,dest)
    im=Image.open(dest); im.load()
    req=read(TILE/f'{stem}.request.json')
    refs=[]
    for i,p in enumerate(req['referenced_image_paths']):
        refs.append({'path':p,'sha256':sha(p),'role':req.get('referenceRoles',{}).get(str(i+1),'See exact input role in prompt')})
    d={'file':str(dest),'sha256':sha(dest),'generatedAt':now(),'nativeDimensions':list(im.size),'format':im.format,'tool':'image_gen__imagegen','route':'builtin','configSnapshot':read(CONFIG),'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed builtin; no model/quality selector or returned model/quality metadata','prompt':str(TILE/f'{stem}.prompt.txt'),'references':refs,'evidence':{'receipt':str(TILE/f'{stem}.receipt.json'),'sourcePath':src},'coordinate':patch(pid),'status':'candidate_pending_geometry_and_seam_review','upsamplingApplied':False}
    write(dest.with_suffix('.png.generation.json'),d)
    prog=read(ZONE/'progress.json'); prog.update(updatedAt=now(),status='native_generation_in_progress',generatedNativeCount=len(list((TILE/'native').glob('*.png'))),currentPatch=pid,nextStep='Inspect native dimensions and geometry; prepare adjacent native-conditioned patch')
    if im.size!=(1254,1254):
        prog['status']='dimension_replanning_required';prog['actualErrors'].append({'at':now(),'nativeDimensions':list(im.size),'message':'Expected 1254 square not returned; must recalculate coverage without enlargement'})
    write(ZONE/'progress.json',prog)
    print(json.dumps({'file':str(dest),'sha256':d['sha256'],'nativeDimensions':list(im.size)},indent=2))
elif mode=='condition':
    pid=sys.argv[2]
    target=patch(pid); targetbox=target['globalBox']
    im=Image.open(target['file']).convert('RGB')
    sources=[]
    for sourcearg in sys.argv[3:]:
        sid,version=sourcearg.split(':');s=patch(sid);sp=TILE/'native'/f'{sid}-{version}.png'
        if not sp.exists(): sp=TILE/'processed'/f'{sid}-{version}.png'
        sim=Image.open(sp)
        assert sim.size==(1254,1254)
        sb=s['globalBox']; b=[max(sb[0],targetbox[0]),max(sb[1],targetbox[1]),min(sb[2],targetbox[2]),min(sb[3],targetbox[3])]
        if b[0]>=b[2] or b[1]>=b[3]: raise ValueError('No overlap')
        crop=[b[0]-sb[0],b[1]-sb[1],b[2]-sb[0],b[3]-sb[1]]
        at=[b[0]-targetbox[0],b[1]-targetbox[1]]
        im.paste(sim.crop(crop),tuple(at))
        sources.append({'source':str(sp),'sha256':sha(sp),'globalOverlapBox':b,'sourceCrop':crop,'pasteAt':at,'role':'exact native overlap constraint; preserve unchanged'})
    out=TILE/'layout-only'/f'{pid}-native-conditioned.png';im.save(out)
    write(out.with_suffix('.png.derivation.json'),{'file':str(out),'sha256':sha(out),'classification':'input-guide only; layout region cannot count as final native detail','operation':'unscaled exact neighbor overlap pasted over layout-only guide','layoutSource':target,'nativeSources':sources})
    print(json.dumps({'file':str(out),'sources':sources},indent=2))
