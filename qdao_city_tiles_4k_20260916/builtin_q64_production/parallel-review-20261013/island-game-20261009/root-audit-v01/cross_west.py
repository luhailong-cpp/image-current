from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime
B=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009')
O=Path(__file__).resolve().parent/'g05-nw-sw-r07-r08-c03-v01'
O.mkdir(exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for ch in iter(lambda:f.read(1048576),b''):h.update(ch)
 return h.hexdigest()
files=[
 ('r07_c03',B/'northwest/tiles/r07_c03_candidate-v1_4096.png'),
 ('r08_c03',B/'southwest/qa/c04-hardseam-north-r08c03-resume-v01-candidate-4096.png'),
 ('r08_c04',B/'southwest/qa/c04-hardseam-north-r08c04-resume-v01-candidate-4096.png')]
sw=json.loads((B.parent/'parallel-review-20261013/island-game-20261009/southwest-audit-v01/inventory.json').read_text(encoding='utf-8-sig'))
t9=next(t for t in sw['tiles'] if t['tileId']=='r09_c03')
files.append(('r09_c03',Path(t9.get('file',t9.get('candidatePath','')))))
inputs=[]
for tid,p in files:
 with Image.open(p) as im:sz=list(im.size)
 assert sz==[4096,4096]
 inputs.append({'tileId':tid,'file':p.as_posix(),'sha256':sha(p),'dimensions':sz})
strips=[]
with Image.open(files[0][1]) as top, Image.open(files[1][1]) as bottom:
 for s in range(4):
  im=Image.new('RGB',(1024,512));im.paste(top.crop((s*1024,3840,(s+1)*1024,4096)),(0,0));im.paste(bottom.crop((s*1024,0,(s+1)*1024,256)),(0,256))
  p=O/f'r07_c03--r08_c03-segment-{s+1}-100pct.png';im.save(p);im.close()
  strips.append({'file':p.as_posix(),'sha256':sha(p),'dimensions':[1024,512],'segment':s+1,'worldBox':[8192+s*1024,28416,8192+(s+1)*1024,28928],'status':'pending_visual_review'})
board=Image.new('RGB',(2048,1024))
for i,e in enumerate(strips):
 with Image.open(e['file']) as im:board.paste(im,((i%2)*1024,(i//2)*512))
board.save(O/'four-segments-board-100pct.png');board.close()
d={'groupCoordinates':[tid for tid,p in files],'inputs':inputs,'focusPair':['r07_c03','r08_c03'],'seams':strips,'crossAtWorld':[12288,28672],'crossStatus':'missing r07_c04; four-way cross cannot be reviewed','operation':'exact native border crops and hard paste; no scaling/blending/repair','formalAccepted':False,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(O/'manifest.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'inputs':inputs,'out':O.as_posix()},ensure_ascii=False))
