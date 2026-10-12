import sys,json,importlib.util
from pathlib import Path
from PIL import Image
tile=Path(__file__).resolve().parents[2]
zone=tile.parent
spec=importlib.util.spec_from_file_location('production_v2',zone/'production_v2.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
identifier=sys.argv[1];pid=identifier[:6];sr=int(pid[1:3]);sc=int(pid[4:6]);tr=5;tc=7
def slot(dr,dc):
 r=(tr-1)*4+sr-1+dr;c=(tc-1)*4+sc-1+dc
 return zone/f'r{r//4+1:02d}_c{c//4+1:02d}',f's{r%4+1:02d}_{c%4+1:02d}'
refs={'target':p.validate_native(tile/'native'/(identifier+'.png'),tile,pid)}
for key,dr,dc in [('north',-1,0),('west',0,-1),('northwest',-1,-1)]:
 td,npid=slot(dr,dc);path=p.selected_path(td,npid)
 if path.exists():refs[key]=p.validate_native(path,td,npid)
out=tile/'qa'/'resume20261012'/identifier
out.mkdir(parents=True,exist_ok=False)
imgs={key:Image.open(ref['file']).convert('RGB') for key,ref in refs.items()}
definitions={
 'north-seam.png':((1024,320),[('north',[115,979,1139,1139],[0,0]),('target',[115,115,1139,275],[0,160])]),
 'west-seam.png':((320,1024),[('west',[979,115,1139,1139],[0,0]),('target',[115,115,275,1139],[160,0])]),
 'northwest-junction.png':((320,320),[('northwest',[979,979,1139,1139],[0,0]),('north',[115,979,275,1139],[160,0]),('west',[979,115,1139,275],[0,160]),('target',[115,115,275,275],[160,160])])}
crops=[]
for name,(size,parts) in definitions.items():
 if any(key not in imgs for key,_,_ in parts):continue
 im=Image.new('RGB',size);records=[]
 for key,box,xy in parts:im.paste(imgs[key].crop(box),tuple(xy));records.append({'source':key,'sourceBox':box,'pasteAt':xy})
 path=out/name;im.save(path);crops.append({'file':str(path),'sha256':p.sha(path),'size':size,'parts':records,'sourceResampled':False})
record={'source':refs['target'],'currentNeighbors':{k:v for k,v in refs.items() if k!='target'},'crops':crops,'operation':'Exact core crop/paste only, no resize/blend/warp','actuallyViewed':False,'formalAccepted':False}
(out/'crop-manifest.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'id':identifier,'out':str(out),'crops':crops}))
