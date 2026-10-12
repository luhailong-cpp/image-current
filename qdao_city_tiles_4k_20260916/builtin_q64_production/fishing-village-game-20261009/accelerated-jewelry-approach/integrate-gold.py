from pathlib import Path
from PIL import Image
import json,hashlib
ROOT=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
proposal_path=ROOT/'r04_c10/repairs/north-gold-v1/proposal.json'
q=read(proposal_path);rgba=Image.open(q['rgbaFile']);assert rgba.size==(280,180)
versions={'r03_c10':(3,4),'r04_c10':(1,2)}
results=[]
for c in q['tileContributions']:
 t=c['tile'];before,after=versions[t]
 src=ROOT/t/'candidate'/f'{t}-4096-candidate-v{before}.png'
 out=ROOT/t/'candidate'/f'{t}-4096-candidate-v{after}.png'
 assert not out.exists()
 im=Image.open(src).convert('RGB');repair=rgba.crop(c['sourceRoiCrop']);im.paste(repair,c['destinationLocalBox'][:2],repair.getchannel('A'));im.save(out)
 rec={'file':str(out),'sha256':sha(out),'dimensions':list(im.size),'operation':'native builtin repair contribution composited with recorded straight-alpha, no resampling','nativePixelsResized':False,'baseCandidate':{'file':str(src),'sha256':sha(src)},'repairProposal':{'file':str(proposal_path),'sha256':sha(proposal_path)},'nativeRepair':{'file':q['nativeFile'],'sha256':q['nativeSha256'],'dimensions':q['nativeDimensions']},'roiContribution':c,'rgbaSha256':q['rgbaSha256'],'maskSha256':q['maskSha256'],'actualModel':None,'actualQuality':None,'formalAccepted':False,'status':'candidate_pending_final_region_seam_review'}
 out.with_suffix('.manifest.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
 preview=im.copy();preview.thumbnail((1024,1024));preview.save(ROOT/t/'qa'/f'candidate-v{after}-preview.png')
 results.append({'tile':t,'file':str(out),'sha256':sha(out)})
print(json.dumps(results))
