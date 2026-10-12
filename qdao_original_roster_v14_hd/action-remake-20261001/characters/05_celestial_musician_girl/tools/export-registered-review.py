"""Apply one common scale and a constant root per entire sequence for review.
Never normalize per-frame bounds/feet; never invent missing frames or approve art.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
reg=load(ROOT/'registration.json')
scale=float(reg['globalScale']);canvas=tuple(reg['outputCanvas']);target=reg['targetRoot']
assert canvas==(1024,1024) and 0<scale<=1
selected=load(ROOT/'candidate-selection.json')
exports=[];checks=[]
for e in selected:
    key=e['action']+'/'+e['direction']
    cfg=reg['sequences'].get(key)
    if not cfg:continue
    sx,sy=cfg['sourceRoot']
    source=ROOT/e['file']
    if sha(source)!=e['sha256']:raise ValueError('Source changed: '+str(source))
    im=Image.open(source).convert('RGBA')
    assert min(im.size)>=1024
    # Premultiplied resampling avoids mixing invisible RGB into visible silk edges.
    matrix=(1/scale,0,sx-target[0]/scale,0,1/scale,sy-target[1]/scale)
    transformed=im.convert('RGBa').transform(canvas,Image.Transform.AFFINE,matrix,Image.Resampling.BICUBIC,fillcolor=(0,0,0,0)).convert('RGBA')
    alpha=transformed.getchannel('A')
    border=max(alpha.crop((0,0,1024,1)).getextrema()[1],alpha.crop((0,1023,1024,1024)).getextrema()[1],alpha.crop((0,0,1,1024)).getextrema()[1],alpha.crop((1023,0,1024,1024)).getextrema()[1])
    source_visible=im.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox()
    x0,y0,x1,y1=source_visible
    projected=[scale*(x0-sx)+target[0],scale*(y0-sy)+target[1],scale*(x1-sx)+target[0],scale*(y1-sy)+target[1]]
    if min(projected[:2])<4 or max(projected[2:])>1020:
        raise ValueError('Uniform scale/root clips visible art; adjust global scale, not this frame: '+key+'/'+str(e['frame'])+' '+str(projected))
    file=f"runtime-review/{e['action']}/{e['direction']}/{e['frame']:02}.png"
    dest=ROOT/file;dest.parent.mkdir(parents=True,exist_ok=True);transformed.save(dest)
    record=file+'.export.json'
    rec={'operation':'uniform_resample_and_constant_sequence_registration','status':'registered_review_not_final_visual_pass','createdAt':datetime.now(timezone.utc).isoformat(),'file':file,'sha256':sha(dest),'width':1024,'height':1024,'mode':'RGBA','source':{'file':e['file'],'sha256':e['sha256'],'nativeSize':[e['nativeWidth'],e['nativeHeight']],'generationRecord':e['generationRecord']},'actualModel':e.get('actualModel'),'actualQuality':e.get('actualQuality'),'transform':{'globalScale':scale,'sourceRoot':cfg['sourceRoot'],'targetRoot':target,'inverseAffine':matrix,'registrationFile':'registration.json','perFrameNormalization':False},'edgeMaxAlpha':border,'projectedVisibleBBox':projected,'finalVisualPassed':False,'clientValidated':False}
    save(ROOT/record,rec)
    exports.append({'action':e['action'],'direction':e['direction'],'frame':e['frame'],'file':file,'generationRecord':record,'sha256':rec['sha256'],'visualStatus':e['visualStatus']+' 已用全角色统一比例、整段固定根导出1024供复核；非自动验收。','sourceSelection':e['file']})
    checks.append({'sequence':key,'frame':e['frame'],'edgeMaxAlpha':border,'sourceVerified':True,'transformConstantWithinSequence':True})
save(ROOT/'registered-selection.json',exports)
save(ROOT/'provenance/registration-export-checks.json',{'count':len(exports),'globalScale':scale,'rootTarget':target,'formalPassed':0,'checks':checks})
print(json.dumps({'registeredReviewExports':len(exports),'expected':196,'finalPassed':0,'globalScale':scale,'edgeAlphaMaximum':max(c['edgeMaxAlpha'] for c in checks)},ensure_ascii=False))

