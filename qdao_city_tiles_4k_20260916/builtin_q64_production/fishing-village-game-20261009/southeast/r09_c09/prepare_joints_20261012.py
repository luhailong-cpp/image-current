from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
T=Path(__file__).resolve().parent
P=T/'repairs';P.mkdir(exist_ok=True)
source=T/'qa/full-resume-20261012-v1/candidate-4096.png'
base=Image.open(source)
refs=json.loads((T/'p14-v1.request.json').read_text())['referenced_image_paths'][1:]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
specs=[('canopy-cross-r2-c2-v1',[1421,1421,2675,2675],'''Repair only the small abrupt rectangular canopy texture/blur step around local x627..950,y490..700, directly above the blue roof ridge. Remove the hard horizontal/vertical source join. Continue the same sharp rounded yellow-green leaves, dark foliage and warm brown branches from surrounding existing canopy into that small soft patch. Keep all canopy/branch silhouettes and locations unchanged; no extra leaf mass or branches. Keep the entire large blue ceramic ridge, its segment seams, highlights and geometry exactly unchanged.'''),('ridge-cross-r3-c3-v1',[2445,2445,3699,3699],'''Repair only the small squared horizontal shadow edge under the large blue roof ridge around local x400..760,y470..620. It is a source-strip artifact. Replace that rectangular tonal step with a naturally tapering coherent shadow following the diagonal ridge and curved blue barrel tiles. Preserve every tile course, joint endpoint, curved tile silhouette, blue glaze highlights and ridge position exactly. Do not add a tile seam or alter the roof plane.''')]
for stem,b,detail in specs:
    target=P/f'{stem}-input.png';base.crop(b).save(target)
    globalbox=[b[0]+32768,b[1]+32768,b[2]+32768,b[3]+32768]
    target.with_suffix('.png.derivation.json').write_text(json.dumps({'file':str(target),'sha256':sha(target),'source':str(source),'sourceSha256':sha(source),'cropTile':b,'globalBox':globalbox,'nativeDimensions':[1254,1254],'resamplingApplied':False,'classification':'exact native joint edit target'},indent=2),encoding='utf-8')
    prompt=f'''Use case: precise-object-edit. Image1 is the exact native1254x1254 EDIT TARGET, a fixed crop of the existing game map at globalbox {globalbox}. {detail} Keep every other pixel subject, layout, scale, camera, contour and surface in place. Keep the outer200px unchanged. Match the original bright daylight rounded Daoist Q painterly finish, sharp broad material detail; no blur, sharpening fringe, crossfade, grain or new objects. Reference2 is full-map LAYOUT ONLY; reference3 independent daylight/material STYLE; reference4 approved Daoist STYLE ONLY, never copy its UI, text, night lighting or characters. No movement, reframing, resizing, new prop, tree, character, lettering, border or grid. Output only the repaired same1254-square.'''
    paths=[str(target)]+refs
    roles={'1':'Exact existing native joint edit target','2':'Authoritative full-map layout only','3':'Independent daylight material style','4':'Approved Daoist painterly style only'}
    req={'prompt':prompt,'referenced_image_paths':paths,'transparent_background':False,'tool':'image_gen__imagegen','route':'builtin','submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None,'createdAt':datetime.now(timezone.utc).isoformat(),'globalBox':globalbox,'tileBox':b,'referenceRoles':roles,'referenceEvidence':[{'path':p,'sha256':sha(p),'role':roles[str(i)]} for i,p in enumerate(paths,1)]}
    (P/f'{stem}.request.json').write_text(json.dumps(req,indent=2),encoding='utf-8')
    (P/f'{stem}.prompt.txt').write_text(prompt,encoding='utf-8')
print(json.dumps({'prepared':[s[0] for s in specs]}))
