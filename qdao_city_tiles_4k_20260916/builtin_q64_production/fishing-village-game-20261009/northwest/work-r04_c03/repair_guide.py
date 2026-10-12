from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
from PIL import Image
import workflow as wf
sr,sc,v,old=map(int,sys.argv[1:5]);wf.prepare(sr,sc,v)
w=Path(__file__).resolve().parent;p=w/'guides'/f'{wf.ident(sr,sc,v)}.positional.png';j=Path(str(p)+'.derivation.json');r=wf.read(j);source=w.parent/'native'/f'{wf.ident(sr,sc,old)}.png';im=Image.open(source).copy()
for e in r['neighbors']:im.paste(Image.open(e['file']).crop(e['sourceCrop']),tuple(e['destinationBox'][:2]))
im.save(p);r['sha256']=wf.sha(p);r['operation']='mechanical native-size repair target with listed actual native overlaps; no scaling or blending';r['derivedFrom'].insert(0,{'file':str(source),'sha256':wf.sha(source),'role':'native repair target'});wf.write(j,r)
