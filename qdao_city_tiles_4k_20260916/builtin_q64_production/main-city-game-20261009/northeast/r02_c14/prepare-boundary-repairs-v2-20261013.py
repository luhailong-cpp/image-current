from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent;Q=T/'qa/local-repair-20261013'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=read(Q/'composition-v3.json');src=Path(base['candidate']);assert sha(src)==base['candidateSha256']
im=Image.open(src)
items=[
('wall-right',[1870,420], "Repair the short flat horizontal foliage cutoff at local y=604 across x=490..835. It is a leftover rectangular transition through otherwise continuous willow leaves. Restore only broken leaf shapes and their immediate color continuity around that horizontal band and the short vertical edge at x=489. Keep all existing branches and leaf arrangement. Do not shift or enlarge leaves."),
('leaf-right',[2842,400], "Repair the short flat horizontal foliage cutoff at local y=624 across x=975..1254, and its small vertical edge at x=975. The artificial band reaches the RIGHT edge; carry the corrected leaves all the way to x=1254. Restore each broken willow leaf along this small band, preserving every other leaf and branch."),
('rock-bottom',[2445,2842], "Repair the L-shaped rectangular material discontinuity across the rock at local y=838, especially where it meets vertical local x=627. This is a paste boundary, not a geological plane. Continue the existing rock facets, small stone grain, shadow and moss through it while preserving the rock silhouette and all cracks. Match the existing neutral gray stone on both sides. Do not warm or recolor the scene.")
]
req0=read(T/'prompts/roof-left-local-v2-20261013.request.json')
reqs=[]
for key,origin,instruction in items:
 name=key+'-local-v2-20261013';box=[*origin,origin[0]+1254,origin[1]+1254];dest=Q/(key+'-input-v2.png');assert not dest.exists();im.crop(box).save(dest)
 req=dict(req0);req['referenced_image_paths']=list(req0['referenced_image_paths']);req['referenced_image_paths'][0]=str(dest)
 req['prompt']="Use case: precise-object-edit. Image 1 is the sole edit target, a finished native map crop. Output opaque 1254x1254 with identical framing, exact geometry and pixel scale. "+instruction+" Keep the rest of image 1 unchanged. In particular preserve top 350 pixels and bottom 200 pixels exactly. This is a narrow local discontinuity repair, not a redraw or global restyle. Preserve crisp original hand-painted texture, existing lighting and hue. References 2/3/4 supply approved map geography, material quality and Daoist Q style only. No resizing, zoom, new objects, text, UI, watermark, blur, noise, plastic sheen or global color change."
 req['repairTarget']={'id':key,'attempt':2,'origin':origin,'input':str(dest),'inputSha256':sha(dest),'crop':box,'baseCandidate':str(src),'baseSha256':sha(src),'issue':instruction}
 (T/'prompts'/(name+'.request.json')).write_text(json.dumps(req,indent=2)+'\n',encoding='utf-8')
 (T/'prompts'/(name+'.prompt.txt')).write_text(req['prompt']+'\n',encoding='utf-8');reqs.append({'id':key,'name':name,'request':str(T/'prompts'/(name+'.request.json'))})
(Q/'second-boundary-repair-plan.json').write_text(json.dumps({'base':base,'repairs':reqs},indent=2)+'\n')
print(json.dumps(reqs))

