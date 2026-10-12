from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parent;T=B/'r13_c13';R=T/'repairs'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
id='umbrella-edge-context-v1'
core=T/'candidate'/'r13_c13-4k-candidate-repaired.png';base=T/'candidate'/'r13_c13-context-4326.png'
context=Image.open(base).convert('RGB');assert context.size==(4326,4326);context.paste(Image.open(core),(115,115))
source=R/f'{id}-source-context-4326.png';context.save(source)
box=[2950,650,4204,1904];sourcebox=[v+115 for v in box]
target=R/f'{id}-target.png';context.crop(sourcebox).save(target)
c=read(B.parent/'production-contract.json');refs=[c['layoutReference'],c['detailStyleReference'],c['primaryStyleReference'],str(target)]
prompt="""Use case: precise-object-edit, native seam geometry repair.
The first3 images are reference ONLY for approved map layout, stone/wood material and primary painting style. THE LAST IMAGE is the only edit target. Return one opaque1254x1254 image. Preserve its exact crop, scale, camera, colors and the good existing parasol.
Repair ONLY the narrow wrong vertical join near target x1100-1150, extending from y430 to1050 along the RIGHT of the parasol. This join contains a bamboo rib that abruptly stops and resumes at the wrong height, and two red/cream rim bands that jump sideways. It is NOT a real object edge: the same single parasol must continue smoothly across this strip into the right-side context. Keep each existing bamboo spoke's centerline, width, shading and straight trajectory continuing from its correct long left/inner section through the right strip to the existing outer endpoint. No truncated rib, duplicate sticks, translucent ghosting or offset replacement. The red/cream curved rim bands and canopy silhouette must each continue smoothly across this narrow join at their exact existing scale.
Keep the one crown, all already-correct spokes on the left and middle, the current white/red canopy, wooden support poles, grey stone floor and shadows fixed. Do not redesign the parasol, shift the crown, fit it inside the crop, zoom out or change the number of ribs. Preserve the outermost32 pixels of this1254 context image unchanged; the wrong formal-tile edge is inside the image at x1146, NOT at this image's outer edge. Only edit the narrow discontinuity and its immediate neighbors. Keep clean bright rounded Taoist chibi illustration, no new objects, text, borders or labels."""
write(R/f'{id}.request.json',{'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False});(R/f'{id}.prompt.txt').write_text(prompt,encoding='utf-8')
write(R/f'{id}.target.json',{'id':id,'operation':'compose current4096 core into original native4326 context, then crop1254 without resampling','source':str(source),'sourceSha256':sha(source),'sourceCanvasSize':[4326,4326],'cropBoxIn4096':box,'cropBoxInSource4326':sourcebox,'width':1254,'height':1254,'resized':False,'target':str(target),'targetSha256':sha(target),'sourceDerivation':{'baseContext':str(base),'baseContextSha256':sha(base),'currentCore':str(core),'currentCoreSha256':sha(core),'corePasteOffset':[115,115]},'references':[{'path':p,'sha256':sha(p),'dimensions':list(Image.open(p).size),'role':r} for p,r in zip(refs,['approved layout','approved material','approved primary style','only edit target: actual native context including outside formal rightedge'])]})
print(json.dumps({'id':id,'target':str(target),'contextBox':sourcebox,'tileBox':box}))

