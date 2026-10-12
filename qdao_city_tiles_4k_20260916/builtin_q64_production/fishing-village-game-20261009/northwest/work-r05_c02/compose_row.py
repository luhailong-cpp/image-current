from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
W=Path(__file__).resolve().parent;B=W.parent;sys.path.insert(0,str(B))
from assemble_r03_c03 import append_hard
r=int(sys.argv[1]);out=W/('row'+str(r)+'-proposal');out.mkdir(exist_ok=True);arrays=[];sources=[]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for c in range(1,5):
 s=json.loads((W/'selections'/f's{r:02d}_s{c:02d}.json').read_text(encoding='utf-8-sig'));p=Path(s['file']);g=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'));arrays.append(np.asarray(Image.open(p).convert('RGB')));sources.append({'sourceId':c,'file':str(p),'sha256':sha(p),'generationRecord':str(p)+'.generation.json','globalNativeBox':g['globalNativeBox']})
arr=arrays[0].copy();ids=np.ones(arr.shape[:2],np.uint16);seams=[]
for i in range(1,4):arr,ids,seam=append_hard(arr,ids,arrays[i],np.full((1254,1254),i+1,np.uint16),'row'+str(r)+'col'+str(i+1));seams.append(seam)
box=[sources[0]['globalNativeBox'][0],sources[0]['globalNativeBox'][1],sources[-1]['globalNativeBox'][2],sources[-1]['globalNativeBox'][3]]
for i,s in enumerate(sources):
 yy,xx=np.where(ids==i+1);assert np.array_equal(arr[yy,xx],arrays[i][yy,xx-i*1024])
p=out/'row.native.png';ip=out/'row.source-id.png';Image.fromarray(arr).save(p);Image.fromarray(ids).save(ip);preview=Image.fromarray(arr);preview.thumbnail((1600,1600));preview.save(out/'row.preview-only.jpg',quality=93)
(out/'assembly.json').write_text(json.dumps({'candidate':{'file':str(p),'sha256':sha(p)},'sourceIdMap':{'file':str(ip),'sha256':sha(ip)},'globalCoreBox':box,'sources':sources,'seams':seams,'proof':{'pixels':ids.size,'mismatches':0},'partialOnly':True},indent=2),encoding='utf-8');print(json.dumps({'row':r,'pixels':ids.size,'mismatches':0}))
