import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib
q=Path(__file__).resolve().parent
pre=sys.argv[1]
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
src=q/(pre+'-candidate-4096.png');new=Image.open(src).convert('RGB');old=Image.open(q/'full-tile-r10_c07-candidate-4096.png').convert('RGB');items=[]
for p in sorted(q.glob('full-tile-r10_c07-*-100pct.png.derivation.json')):
 d=json.loads(p.read_text());box=d['sourceBox'];im=new.crop(box);changed=ImageChops.difference(im,old.crop(box)).getbbox() is not None
 item={'id':p.name.split('full-tile-r10_c07-')[1].split('-100pct')[0],'baseQA':d,'changed':changed}
 if changed:
  dst=q/(pre+'-'+item['id']+'-100pct.png');im.save(dst);item['qa']=ref(dst);item['sourceBox']=box
 items.append(item)
for rid,box in [('curb',[650,2500,1904,3754]),('wood',[2842,1550,4096,2804])]:
 dst=q/f'{pre}-{rid}-composed-100pct.png';new.crop(box).save(dst)
 Path(str(dst)+'.derivation.json').write_text(json.dumps({'source':ref(src),'sourceBox':box,'operation':'integer native crop only','sha256':ref(dst)['sha256']},indent=2))
(q/(pre+'-review-worklist.json')).write_text(json.dumps({'source':ref(src),'items':items},indent=2))
print(json.dumps({'changed':[x['id'] for x in items if x['changed']],'unchanged':len([x for x in items if not x['changed']])}))
