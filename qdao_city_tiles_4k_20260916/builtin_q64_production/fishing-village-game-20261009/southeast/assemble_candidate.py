"""Unscaled core-only candidate assembly. Never confers seam/formal acceptance."""
from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
z=Path(__file__).resolve().parent
selection=json.loads((z/'selected-patches.json').read_text(encoding='utf-8-sig'))
t=z/selection['tile'];out=t/'candidate';out.mkdir(exist_ok=True)
canvas=Image.new('RGB',(4096,4096));sources=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for sr in range(1,5):
    for sc in range(1,5):
        pid=f'p{sr}{sc}';p=t/selection['patches'][pid];im=Image.open(p).convert('RGB')
        assert im.size==(1254,1254)
        at=[(sc-1)*1024,(sr-1)*1024]
        canvas.paste(im.crop((115,115,1139,1139)),tuple(at))
        rec=str(p)+('.generation.json' if p.parent.name=='native' else '.derivation.json')
        assert Path(rec).exists()
        sources.append({'patch':pid,'file':str(p),'sha256':sha(p),'record':rec,'nativeSize':[1254,1254],'sourceCore':[115,115,1139,1139],'destination':[*at,at[0]+1024,at[1]+1024]})
target=out/'r10_c09-unscaled-candidate.png';canvas.save(target)
meta={'file':str(target),'sha256':sha(target),'createdAt':datetime.now(timezone.utc).isoformat(),'dimensions':[4096,4096],'classification':'candidate_pending_internal_and_external_seam_validation','tile':'r10_c09','globalCoreBox':[32768,36864,36864,40960],'operation':'16 native1024 cores cropped from1254 sources, hard cut at overlap midpoints, no resizing/blending/warping','upsampling':False,'blending':False,'pixelCoverage':16777216,'uncoveredPixels':0,'derivedFrom':sources,'internalSeams':'pending','externalSeams':'unverified','formalAccepted':False,'capacity5000Validated':False,'clientMappingValidated':False}
target.with_suffix('.png.derivation.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
preview=out/'r10_c09-QA-preview-1024.png';canvas.resize((1024,1024),Image.Resampling.LANCZOS).save(preview)
preview.with_suffix('.png.derivation.json').write_text(json.dumps({'classification':'downsampledQApreviewONLY','derivedFrom':{'file':str(target),'sha256':meta['sha256']},'operation':'4xdownsampleforoverview; notnative/final'},indent=2),encoding='utf-8')
prog=json.loads((z/'progress.json').read_text(encoding='utf-8-sig'));prog.update(updatedAt=meta['createdAt'],assembled4kCandidateCount=1,complete4kCount=0,formalAcceptedCount=0,status='full_tile_seam_QA_in_progress',currentPatch=None,nextStep='Inspect24 full native internal joins and9 crossings; repair structure with builtin before any acceptance or outward expansion')
(z/'progress.json').write_text(json.dumps(prog,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'candidate':str(target),'sha256':meta['sha256'],'nativeCoverage':meta['pixelCoverage'],'complete4kCount':0,'formalAcceptedCount':0},indent=2))
