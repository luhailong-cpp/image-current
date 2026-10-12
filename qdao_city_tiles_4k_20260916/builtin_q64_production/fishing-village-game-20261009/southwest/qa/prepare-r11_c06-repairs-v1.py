import sys
sys.dont_write_bytecode=True
import json,importlib.util
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':prod.sha(p)}
a=read(z/'qa/full-tile-r11_c06-assembly.json');styles=read(z/'references.json')
issues=[{"id":"A","issue":"v1024 part02 table wood color zipper seam and part03 under-table ground/shadow band","approxCore":[950,1500],"repairNeeded":True},{"id":"B","issue":"v2048 part02 clear jagged brightness boundary through porcelain bowl and tabletop","approxCore":[2048,1150],"repairNeeded":True},{"id":"C","issue":"v3072 part04 stone at stair foot clipped by vertical seam; nearby sand color seam","approxCore":[3010,2650],"repairNeeded":True},{"id":"D","issue":"h1024 part04 tall stall post has abrupt horizontal brightness/woodgrain transition","approxCore":[2675,980],"repairNeeded":True},{"id":"E","issue":"h2048 part03 rear right table leg horizontal brown color jump","approxCore":[2150,2020],"repairNeeded":True}]
audit={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r11_c06','status':'targeted_repairs_required','source':ref(z/'qa/full-tile-r11_c06-assembly.json'),'compositionViewed':ref(z/'qa/r11_c06-resume-composition-preview-v1.png'),'nativeCropsViewed':a['qa'],'viewedCount':39,'issues':issues,'notes':'All 39 native crops directly visually inspected. Broad composition and lane geometry consistent. Local seams below require native repairs; remaining areas acceptable.'}
prod.write(z/'qa/r11_c06-internal-visual-audit-v1.json',audit)
jobs=[]
specs=[('A',450,1200,[300,180,810,1160],80,'Repair only the visible jagged vertical brightness boundary near image x=500 through the rounded wooden table rim and ground underneath it. Make wood grain and shading continuous and the ground shadow smooth without moving anything. Keep mooncake contours, all legs, table silhouette and shadow silhouette exactly aligned.'),('B',1421,550,[330,110,870,1170],80,'Repair only the jagged brightness/color boundary near image x=650 across the wooden tabletop and the blue-and-white porcelain bowl. The bowl must have continuous smooth glaze lighting and continuous blue floral linework, including its gold rim, with no cut or doubled rim. Preserve the exact bowl ellipse, ornament positions, table, mooncake and red tassel. Do not redraw or reposition the bowl.'),('C',2445,2050,[370,380,850,1150],80,'Repair the visible vertical patch boundary near image x=565 at the foot of the stone stairs: reconnect the small gray pebble that has been clipped in half and match the warm sandy ground texture and brightness continuously. Preserve every stair, curb stone, wooden post and grass tuft; do not add stones or modify stair geometry.'),('D',2050,450,[450,250,850,800],65,'Repair only the abrupt horizontal woodgrain/brightness transition at image y=530 on the tall orange-brown wooden stall post near image x=600. Continue the same vertical wood grain and smooth consistent light on each face. Preserve the silhouette and width of the post, exact table edges, plants and stone road.'),('E',1450,1450,[420,350,860,850],65,'Repair only the abrupt horizontal brown color transition at image y=570 on the right-hand face of the wooden table leg near image x=700. Continue matching wood grain and smoothly consistent lighting. Preserve the exact leg silhouette, ground, crossbar, shadows and foliage, without altering any object placement.')]
ctx=Image.open(z/'qa/full-tile-r11_c06-context-native.png')
for rid,x,y,bounds,margin,desc in specs:
 stem=f'r11_c06_repair_{rid}_v1';source=z/'qa'/f'{stem}-source-native.png'
 assert not source.exists(),source
 ctx.crop((x+115,y+115,x+1254+115,y+1254+115)).save(source)
 refs=[{'path':source.as_posix(),'role':'edit target: exact native 1254 crop from current assembly'},styles[1],styles[2]]
 prompt='Use case: precise-object-edit. Asset: seamless native 1254 x 1254 game-map repair patch. Image 1 is the exact edit target and controls all geometry and pixel placement; images 2 and 3 are style references only. '+desc+' Match the target daylight, rounded painterly Daoist Q art and its existing palette exactly. Preserve outer 180 pixels and all unaffected imagery; edit only the stated defect. Return the same square crop at native 1254 x 1254 with no zoom, crop, resize, camera shift, new objects, text, UI, border or watermark. Do not change overall brightness. The repair will be adopted only within a closed local region.'
 (z/'native'/f'{stem}.prompt.txt').write_text(prompt,encoding='utf-8')
 req={'stem':stem,'tile':'r11_c06','patch':f'repair_{rid}','coordinates':{'role':'localized native seam repair','tile':'r11_c06','tileContextBox':[x,y,x+1254,y+1254],'globalContextBox':[20480+x,40960+y,20480+x+1254,40960+y+1254],'nativeSize':[1254,1254]},'references':refs,'submittedParameters':{'model':None,'quality':None,'transparent_background':False}}
 prod.write(z/'native'/f'{stem}.request.json',req)
 jobs.append({'id':rid,'stem':stem,'source':ref(source),'tileContextBox':[x,y,x+1254,y+1254],'repairBounds':bounds,'margin':margin,'prompt':prompt,'references':[r['path'] for r in refs]})
prod.write(z/'qa/r11_c06-repair-jobs-v1.json',jobs)
print(json.dumps([{'id':j['id'],'source':j['source']['path']} for j in jobs]))
