from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
T=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=T/'native/p31-v2.png';s=T/'native/p41-v4.png';a=Image.open(base).convert('RGBA');n=Image.open(s).convert('RGBA')
# Correct input-only whole-post alignment to the exact selected lower native center.
part=a.crop((317,200,760,788));arr=np.array(part);mask=((arr[:,:,0]>arr[:,:,2]*1.2)&(arr[:,:,0]>65));part.putalpha(Image.fromarray(np.uint8(mask)*255))
alpha=a.getchannel('A');alpha.paste(0,(317,200,860,788));a.putalpha(alpha);a.alpha_composite(part,(417,200))
# Background and horizontal arm guide pixels remove the obsolete wider draft shaft.
a.paste(a.crop((300,740,433,817)),(435,740))
a.paste(a.crop((275,817,408,990)),(435,817))
a.paste(a.crop((302,990,435,1024)),(435,990))
for y in range(740,1024,115):a.paste(n.crop((568,115,704,115+min(115,1024-y))),(568,y))
a.paste(n.crop((0,0,1254,230)),(0,1024))
out=T/'layout-only/p31-v3-whole-post-core-aligned.png';a.save(out)
old=json.loads((T/'p31-v2.request.json').read_text(encoding='utf-8-sig'))
prompt='''Use case: precise-object-edit. Image1 is the exact ORIGINAL1254square target. Render this same guide into one finished sharp native1254square RGB patch. Preserve all visible objects and their EXACT silhouettes and positions in image1. The entire existing post is now aligned correctly in the guide: gold finial and cap centered over the NARROW straight wood shaft x568..704; horizontal wood arm passes behind it. Keep this guide shaft width, leftedge568 and rightedge704 throughout y740..1254. Do not widen it, move it left, add a second old shaft, recenter the composition or revert to the earlier draft. Left of568 below the cap is gray stone background except the horizontal arm y817..990. The shaft is the narrow dark strip shown in the guide, not a broad column. Keep its exact fixed silhouettes.
Change only guide artifacts: fill transparent background around the gold cap with same flat bluegray stone paving; make pasted stone grout and horizontal crossarm grain connect naturally, remove guide cut lines; make the repeated narrow native wood strip coherent natural wood grain while maintaining its width and center. Keep every existing lantern and lower230px sharp native geometry unchanged. Corecuts115 and1139px; connect down into the EXACT lower-neighbor shaft and red/gold lanterns with no width step or rectangular boundary. Do not move or invent objects, hooks or ornaments. Same bright clear daylight, broad crisp Daoist Q painterly material density. Image2 fullmap layout/context only,3 independent daylight material style,4 approved Daoist Q style only. Flat paving background only; no wall, plant, new crossbar, building, UI, letters, characters, border or watermark. Output exact1254square originalfootprint, no resizing, zoom or crop.'''
req={**old,'prompt':prompt,'referenced_image_paths':[str(out)]+old['referenced_image_paths'][1:]};req['referenceEvidence']=[dict(path=p,sha256=sha(p),role=req['referenceRoles'][str(i)]) for i,p in enumerate(req['referenced_image_paths'],1)]
(T/'p31-v3.prompt.txt').write_bytes(prompt.encode('utf-8'));(T/'p31-v3.request.json').write_text(json.dumps(req,indent=2),encoding='utf-8')
Path(str(out)+'.derivation.json').write_text(json.dumps(dict(file=str(out),sha256=sha(out),classification='input guide only, never final art',operation='Correct whole-post input silhouette to actual native lower center; native unscaled guide copies, opaque background cleanup, alpha background around moved draft cap',derivedFrom=[dict(file=str(p),sha256=sha(p)) for p in [base,s]],actualLowerPost=[568,704],inputOnlyDraftCapTranslation=[100,0],noFinalSourcePixelsSelected=True),indent=2),encoding='utf-8')
print(str(out))
