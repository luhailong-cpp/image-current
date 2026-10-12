from pathlib import Path
import json,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
inv=json.loads((ROOT/'candidate-inventory.json').read_text(encoding='utf-8-sig'))
cfg=json.loads((ROOT/'candidate/battle-registration.json').read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for group,reg in cfg['groups'].items():
    for f in inv['groups'].get(group,[]):
        src=ROOT/f['url'][3:]
        im=Image.open(src).convert('RGBA')
        assert im.size==(1254,1254)
        out=Image.new('RGBA',(1024,1024))
        out.alpha_composite(im.resize((860,860),Image.Resampling.LANCZOS),tuple(reg['translation']))
        dest=ROOT/'candidate'/group/f"{f['frame']:02}.png"
        dest.parent.mkdir(parents=True,exist_ok=True);out.save(dest)
        meta={'file':dest.relative_to(ROOT).as_posix(),'sha256':sha(dest),'width':1024,'height':1024,'mode':'RGBA','status':'candidate-export-not-visually-approved','derivedFrom':[{'file':src.relative_to(ROOT).as_posix(),'sha256':sha(src),'generationRecord':str(src.relative_to(ROOT))+'.generation.json'}],'operation':{'type':'uniform-whole-canvas-resample-and-group-fixed-translation','newPoseGenerated':False,'scale':860/1254,'translation':reg['translation'],'rootTarget':[512,942],'basis':reg['basis'],'perFrameLowestFootAlignment':False,'perFrameBBoxScaling':False},'visualAcceptance':False,'dynamicAcceptance':False}
        Path(str(dest)+'.generation.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        rows.append({'group':group,'frame':f['frame'],'file':meta['file'],'source':src.relative_to(ROOT).as_posix(),'sourceSHA':sha(src)})
(ROOT/'candidate/battle-export-inventory.json').write_text(json.dumps({'status':'fixed-registration-candidates','count':len(rows),'frames':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'battleCandidateExports':len(rows)}))

