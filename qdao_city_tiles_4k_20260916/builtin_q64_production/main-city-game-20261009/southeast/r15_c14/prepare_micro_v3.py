from pathlib import Path
import json,hashlib,datetime
from PIL import Image,ImageDraw
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r15_c14');D=T/'repairs/internal-micro-v3-20261012';D.mkdir()
B=T/'candidate/r15_c14-4k-internal-repair-v2-20261012.png';box=[1210,1950,2464,3204]
target=D/'target-native-1254.png';Image.open(B).crop(box).save(target)
regions=[[1440,2160,1650,2350],[2120,2480,2260,2630]]
mask=Image.new('L',(1254,1254));draw=ImageDraw.Draw(mask)
for x0,y0,x1,y1 in regions:draw.rectangle([x0-box[0],y0-box[1],x1-box[0]-1,y1-box[1]-1],fill=255)
mp=D/'edit-mask-1254.png';mask.save(mp)
refs=json.loads((T/'records/p01_01_v20261012T135016_73f165cf.request.json').read_text())['referenced_image_paths'][:3]
prompt='Use case: precise-object-edit. Last image is the edit target: actual 1254 x 1254 native stone pavement crop. First three images are material references only. Second-last image is a white-island edit mask: change ONLY the two small white islands, keep every other pixel unchanged. Do not resize, reframe, warp or recolor. UPPER LEFT editable island: erase the small faded blue tint on the large pale slab immediately above the diagonal row of small blue paving blocks. Continue the same pale slab texture, preserving its complete existing diagonal grout boundary, so the blue row begins at its existing complete closed joint. LOWER RIGHT editable island: repair the tiny rectangular notch in the left edge of the blue inlay row. Join the upper edge endpoint to the slightly left-offset lower endpoint with a short natural angled bevel. Preserve BOTH endpoints and the lower strip width exactly; a slight taper in this one block is intended. Do NOT straighten, reposition, narrow or redraw the whole blue strip. The local transition must fit the existing top and bottom geometry without moving it. No new slab, props or text.'
req={'prompt':prompt,'referenced_image_paths':refs+[str(mp),str(target)],'transparent_background':False}
def rec(p):return {'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
(D/'request.json').write_text(json.dumps(req,indent=2));(D/'prompt.txt').write_text(prompt)
(D/'preparation.json').write_text(json.dumps({'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base':rec(B),'targetCrop':box,'applyRegions':regions,'references':[rec(p) for p in req['referenced_image_paths']],'request':rec(D/'request.json'),'nativeSize':[1254,1254],'noResize':True},indent=2))
print(str(D))

