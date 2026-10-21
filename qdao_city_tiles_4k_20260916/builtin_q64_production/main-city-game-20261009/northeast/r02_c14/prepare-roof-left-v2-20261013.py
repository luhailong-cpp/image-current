from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
T=Path(__file__).resolve().parent;Q=T/'qa/local-repair-20261013'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=read(Q/'composition-v2.json');src=Path(base['candidate']);assert sha(src)==base['candidateSha256']
box=[0,2445,1254,3699];dest=Q/'roof-left-input-v2.png';assert not dest.exists()
Image.open(src).crop(box).save(dest)
name='roof-left-local-v2-20261013'
req=read(T/'prompts/roof-corner-local-v20261013.request.json')
req['prompt']="Precise local repair of image 1, a native finished map crop. Return one opaque 1254x1254 image, EXACT crop and scale. The defect is a straight horizontal rectangular color/material cut across cyan roof tiles at y=627, from x=0 to about x=600. Remove that artificial rectangular step by repainting ONLY a narrow strip around the discontinuity. Continue the existing ceramic cylinders, ridges, crackle and highlight direction smoothly through it; do not change tile positions, scale, curves or row counts. On the far left the defect reaches the image edge, so carry the corrected ceramic right to x=0. Also eliminate any residual vertical paste edge near x=551 in that same neighborhood. Keep top 350 pixels, bottom 250 pixels, and rightmost 200 pixels unchanged. Preserve gold hip ridge, spiral corner ornament, all gold flower tile ends and red wooden framing exactly. Preserve sharp existing hand-painted texture, hue and daylight. References 2/3/4 define established map geography, material quality and Daoist Q style; image 1 is the sole edit target. No new objects, text, UI, watermark, crop shift, zoom, soft focus, blur, lighting changes or global recoloring."
req['referenced_image_paths'][0]=str(dest)
req['repairTarget']={'id':'roof-left','attempt':2,'origin':box[:2],'input':str(dest),'inputSha256':sha(dest),'crop':box,'baseCandidate':str(src),'baseSha256':sha(src),'issue':'remaining horizontal roof material step at tile y3072 on west side'}
(T/'prompts'/(name+'.request.json')).write_text(json.dumps(req,indent=2)+'\n',encoding='utf-8')
(T/'prompts'/(name+'.prompt.txt')).write_text(req['prompt']+'\n',encoding='utf-8')
review={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'candidate':str(src),'candidateSha256':sha(src),'status':'improved_candidate_pending_local_repair','internalPassed4kCount':0,'formalAcceptedCount':0,'visualWindows':[str(Q/(i+'-composed-v2.png')) for i in ['wall-leaves','leaf-bands','roof-corner','rock-corner']],'findings':[{'id':'wall-leaves','status':'improved_outer_boundary_pending','detail':'Original flat wall/leaf cutoff removed; faint straight border variation remains at top and right repair boundaries.'},{'id':'leaf-bands','status':'improved_outer_boundary_pending','detail':'Original L-shaped clipped bands repaired; minor leaf/tone mismatch at rightmost repair edge remains.'},{'id':'roof-corner','status':'P2_remaining','detail':'Central crossed discontinuity improved, but horizontal material step remains across west roof at tile y3072. Second native edit planned on shifted crop.'},{'id':'rock-corner','status':'improved_outer_boundary_pending','detail':'Rock geometry and central quadrant join continuous, but outer bottom edge retains tone difference.'}],'composition':str(Q/'composition-v2.json'),'sourceHashesUnchanged':True}
(Q/'visual-review-v2.json').write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'input':str(dest),'request':str(T/'prompts'/(name+'.request.json'))}))

