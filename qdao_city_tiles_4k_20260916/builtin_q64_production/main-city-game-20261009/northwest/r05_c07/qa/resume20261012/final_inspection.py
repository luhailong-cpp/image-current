import json,importlib.util
from pathlib import Path
from PIL import Image
tile=Path(__file__).resolve().parents[2];zone=tile.parent
spec=importlib.util.spec_from_file_location('production_v2',zone/'production_v2.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
out=tile/'qa'/'resume20261012'/'final-inspection';out.mkdir(exist_ok=False)
refs={}
for label,pid in [('gap-upper','s01_04'),('gap-lower','s02_04'),('blue-upper','s01_03'),('blue-lower','s02_03')]:
 ref=p.validate_native(p.selected_path(tile,pid),tile,pid);refs[label]=ref
 r=int(pid[1:3]);c=int(pid[4:6]);ox=(c-1)*1024-115;oy=(r-1)*1024-115
 box=[3090,945,3250,1110] if label.startswith('gap') else [1980,950,2370,1130]
 im=Image.open(ref['file']);im.crop((box[0]-ox,box[1]-oy,box[2]-ox,box[3]-oy)).save(out/(label+'.png'))
west={};east={}
for r in range(1,5):
 for side,td,pid,target in [('west',zone/'r05_c06',f's{r:02d}_04',west),('east',tile,f's{r:02d}_01',east)]:
  ref=p.validate_native(p.selected_path(td,pid),td,pid);target[r]={'ref':ref,'im':Image.open(ref['file']).convert('RGB')};refs[f'{side}-{r}']=ref
 im=Image.new('RGB',(320,1024));im.paste(west[r]['im'].crop((979,115,1139,1139)),(0,0));im.paste(east[r]['im'].crop((115,115,275,1139)),(160,0));im.save(out/f'west-segment{r:02d}.png')
for r in range(1,4):
 im=Image.new('RGB',(320,320))
 for rr,yy,cy in [(r,0,979),(r+1,160,115)]:
  im.paste(west[rr]['im'].crop((979,cy,1139,cy+160)),(0,yy));im.paste(east[rr]['im'].crop((115,cy,275,cy+160)),(160,yy))
 im.save(out/f'west-junction-y{r*1024}.png')
record={'sources':refs,'operation':'Exact native same-coordinate crops and external core paste; no resize, blend or warp','cropHashes':{f.name:p.sha(f) for f in out.glob('*.png')},'actuallyViewed':False,'formalAccepted':False}
(out/'manifest.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(out)

