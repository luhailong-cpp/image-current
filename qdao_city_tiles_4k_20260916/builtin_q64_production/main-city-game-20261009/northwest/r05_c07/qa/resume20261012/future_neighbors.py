import sys,json,importlib.util
from pathlib import Path
from PIL import Image
t=Path(__file__).resolve().parents[2];z=t.parent
spec=importlib.util.spec_from_file_location('p',z/'production_v2.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
id=sys.argv[1];pid=id[:6];r=int(pid[1:3]);c=int(pid[4:6]);target=p.validate_native(t/'native'/(id+'.png'),t,pid)
out=t/'qa/resume20261012'/id;imgs={'target':Image.open(target['file']).convert('RGB')};refs={'target':target}
for label,rr,cc in [('west',r,c-1),('east',r,c+1),('south',r+1,c),('southwest',r+1,c-1),('southeast',r+1,c+1)]:
 if not(1<=rr<=4 and 1<=cc<=4):continue
 npid=f's{rr:02d}_{cc:02d}';path=p.selected_path(t,npid)
 if path.exists():ref=p.validate_native(path,t,npid);refs[label]=ref;imgs[label]=Image.open(ref['file']).convert('RGB')
defs={'east-seam':((320,1024),[('target',[979,115,1139,1139],[0,0]),('east',[115,115,275,1139],[160,0])]),'south-seam':((1024,320),[('target',[115,979,1139,1139],[0,0]),('south',[115,115,1139,275],[0,160])]),'southwest-junction':((320,320),[('west',[979,979,1139,1139],[0,0]),('target',[115,979,275,1139],[160,0]),('southwest',[979,115,1139,275],[0,160]),('south',[115,115,275,275],[160,160])]),'southeast-junction':((320,320),[('target',[979,979,1139,1139],[0,0]),('east',[115,979,275,1139],[160,0]),('south',[979,115,1139,275],[0,160]),('southeast',[115,115,275,275],[160,160])])}
record={'refs':refs,'crops':[]}
for name,(size,parts) in defs.items():
 if any(k not in imgs for k,_,_ in parts):continue
 im=Image.new('RGB',size)
 for k,box,xy in parts:im.paste(imgs[k].crop(box),xy)
 path=out/(name+'.png');assert not path.exists();im.save(path);record['crops'].append({'file':str(path),'sha256':p.sha(path),'parts':parts,'sourceResampled':False})
(out/'additional-neighbors.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record['crops']))

