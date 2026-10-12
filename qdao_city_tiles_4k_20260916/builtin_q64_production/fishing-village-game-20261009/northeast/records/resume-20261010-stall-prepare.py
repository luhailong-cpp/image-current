from pathlib import Path
from PIL import Image
import json,hashlib,datetime
B=Path(__file__).resolve().parent.parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p,role): return {'path':str(p),'sha256':sha(p),'role':role}
def write(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
base=B/'native/p34-p44-repair-target-v1.png'
layout=B/'guides/p34-p44-repair-layout-only-v1.png'
g=Image.open(layout).convert('RGB')
n=Image.open(base).convert('RGB')
# Reference preparation only: retain measured native boundary rectangles, no final art editing.
rects=[[0,0,180,1254],[180,0,580,180],[180,1120,330,1254]]
for box in rects: g.paste(n.crop(box),(box[0],box[1]))
p=B/'guides/resume-20261010-stall-layout-native-guide-v1.png';g.save(p)
write(str(p)+'.derived.json',{'purpose':'GENERATION GUIDE ONLY, never final game pixels','worldBox':[48013,22925,49267,24179],'size':[1254,1254],'base':rec(layout,'exact layout-only global crop'),'nativeBoundarySource':rec(base,'original selected p34/p44 native plane'),'nativeRectangles':rects,'operation':'opaque integer crop/paste; exact layout replaces entire misplaced stall and its old footprint; no final art created','formalAccepted':False})
contract=json.loads((B.parent/'production-contract.json').read_text(encoding='utf-8'))
paths=[contract['layoutReference'],contract['detailStyleReference'],contract['primaryStyleReference'],str(p),str(B/'guides/p34-p44-repair-reference-v1.png')]
roles=['authoritative full-map layout','independent material/style close-up only','Q Daoist primary style only; ignore UI/night','primary square sketch-to-render target; correct stall placement plus native floor boundary anchors','LEFT exact same layout-only crop; RIGHT native fish painting style, not placement']
prompt='''Use case: sketch-to-render. Produce ONE square 1254 x 1254 native game-map detail image. Follow image 4 as the composition and edge-connection blueprint; image 5 LEFT repeats its exact correct spatial layout. This is a fresh detailed reconstruction of the small wooden fish-display stall, not an enlargement. The blurry central/right image-4 content is an exact layout guide to render sharply; the crisp left strip and small top-left/bottom-left corners are native surrounding floor anchors to preserve seamlessly.
Coordinates are measured from the upper-left of this 1254 square: the front rim has its LEFTMOST protruding tip at about (410,380), and slopes down-right through (850,570) to the right edge about y760. The front-left support is a complete long vertical wooden post centered x570, descending from under the rim around y480 to its foot at y980. The front apron and lower horizontal wooden brace continue from this long support down-right, and are cropped naturally by the RIGHT edge. Do not shorten or move the post to the upper-right. Keep the correct complete silhouette and shadow. Fish fill only the existing tabletop region above this diagonal front rim. Render blue/silver tapered fish with readable gills, fins, overlapping scales and gentle volume, resembling the RIGHT panel of image 5, never blue balls. Continue the partial red fish at top-right. Do not add a new freestanding capped pillar. Do not center the stall or fit the full stall into the square; its right part extends beyond the image edge.
Keep the native floor anchors of image4 in the same coordinates: full left180 strip, top-left rectangle x180..580/y0..180, bottom-left rectangle x180..330/y1120..1254. Join floor smoothly to them without a straight band, and preserve the gray-to-warm stone-paving transition entering from the lower-left. Stone stays pale natural gray/blue-gray with quiet low-contrast joints, warm stone at lower right as in the original surroundings. Match existing isometric camera, object scale, light direction, rounded bright clean Daoist Q painterly game-art finish. Image1 is global layout only; image2 materials only, do not copy temple buildings; image3 style only, do not copy text/UI/night. No added objects, buildings, trees, lanterns, characters, UI, letters, numbers, borders or watermark. Return only the fully painted square, no multi-panel diagram. Every final detail must be newly rendered native image detail; no blurry layout pixels in the result.'''
pf=B/'records/resume-20261010-stall-v1.prompt.txt';pf.write_text(prompt,encoding='utf-8')
req={'tool':'image_gen.imagegen','route':'builtin','submittedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'promptFile':str(pf),'promptSha256':sha(pf),'references':[rec(q,r) for q,r in zip(paths,roles)],'worldBox':[48013,22925,49267,24179],'target':{'model':'gpt-image-2.5-sunburst','quality':'max'},'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'expectedNativeSize':[1254,1254]}
write(B/'records/resume-20261010-stall-v1.submission.json',req)
print(json.dumps({'guide':str(p),'submission':str(B/'records/resume-20261010-stall-v1.submission.json')}))
