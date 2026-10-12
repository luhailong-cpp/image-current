from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[2];Q=Path(__file__).resolve().parent
assert __import__('os').environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pid='r09_c11_roof_color_lower_v01'
base=[R/'tiles/r09_c11.candidate-v04.png',R/'tiles/r09_c12.candidate-v08.png'];upper=R/'native/r09_c11_roof_color_upper_v01.png'
assert sha(upper)=='c8acca4ebdb37ab685cc976cd21dd666ce486c34b07f6b31b5c3e80e6cee9872'
canvas=Image.new('RGB',(8192,4096));canvas.paste(Image.open(base[0]).convert('RGB'),(0,0));canvas.paste(Image.open(base[1]).convert('RGB'),(4096,0))
img=canvas.crop((3300,600,4554,1854));anchor=Image.open(upper).convert('RGB').crop((0,600,1254,1254));assert anchor.size==(1254,654);img.paste(anchor,(0,0))
f=R/'guides'/f'{pid}.native-context.png';assert not f.exists();img.save(f)
wr(Path(str(f)+'.generation.json'),{'file':str(f),'sha256':sha(f),'operation':'Exact native candidate crop with upper source bottom654 rows pasted into top654; no resize or changed RGB','bases':[{'file':str(b),'sha256':sha(b)} for b in base],'baseTwoTileCanvasCrop':[3300,600,4554,1854],'placements':[{'source':str(upper),'sha256':sha(upper),'sourceCrop':[0,600,1254,1254],'destination':[0,0],'destinationBox':[0,0,1254,654]}],'usableAsFinalArt':False})
refs=[{'file':str(f),'sha256':sha(f),'role':'EDIT TARGET: true world-aligned1254 crop with top654 from accepted upper native; unscaled exact geometry authority.'}]+rd(R/'references.json')
prompt="""Use case: precise-object-edit. Return one opaque native1254x1254 crop by editing attached image1 for our continuous daylight Q Daoist game roof. Last3 images are LAYOUT ONLY, MATERIAL ONLY and PAINTING STYLE ONLY. No whole-island content, no UI.
Image1 is the exact native crop immediately BELOW our repaired upper roof. Its TOP654 rows y0..653 are the true unscaled bottom654 rows of the new upper image. This is a fixed anchor: preserve all its curved tile outlines, rounded rim positions, white highlights and color gradients. Never move or fit it elsewhere. Continue those SAME long blue curved ceramic tiles into y654..1253, matching their cylindrical cyan-to-cobalt shading and bright painted detail smoothly. The old incorrect straight vertical pale/deep-blue source stripe at image x514 below the anchor must be eliminated completely. The mechanical transition at y654 is NOT a real roof edge: do not reproduce any horizontal color line there. Repaint COMPLETE existing lower tile surfaces and their rounded gold-medallion ends so blue tone, groove tangents and row phase connect naturally from the true top anchor. No new straight source boundaries.
Keep LEFT115 and RIGHT115 as precise continuity geometry and color anchors; keep BOTTOM115 and all existing red timber/wall pixels unchanged. Keep all gold circular tile-end medallions in the same place and shape. Preserve original tile count, white rim curves, black gutter spacing, diagonal roof perspective, scale and daylight. No new roof courses, ornaments, extra objects, text, people, blur, feathering, pixel resizing or photographic textures. Edit the blue roof material only where needed to remove the stripe. Do not recolor the wood underneath.
Native crop origin relative r09c11 is[3300,600], global[44260,33368]. r09c12 boundary is local x796. The old bad colorstripe is localx514. This is the SECOND and final native repair attempt this round; a single complete crop, not a comparison panel."""
pf=R/'prompts'/f'{pid}.prompt.txt';assert not pf.exists();pf.write_text(prompt,encoding='utf-8')
req={'id':pid,'promptPath':str(pf),'promptSha256':sha(pf),'references':refs,'originRelativeR09c11':[3300,600],'nativeGlobalBox':[44260,33368,45514,34622],'baseCandidates':[{'file':str(b),'sha256':sha(b)} for b in base],'upperNative':str(upper),'upperNativeSha256':sha(upper),'upperOverlapSourceCrop':[0,600,1254,1254],'upperOverlapDestination':[0,0,1254,654],'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None}
wr(R/'prompts'/f'{pid}.request.json',req)
print(json.dumps({'pid':pid,'toolArgs':{'prompt':prompt,'referenced_image_paths':[a['file'] for a in refs],'transparent_background':False}},ensure_ascii=False))

