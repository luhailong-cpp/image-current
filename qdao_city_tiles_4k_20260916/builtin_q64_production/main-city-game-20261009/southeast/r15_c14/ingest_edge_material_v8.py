from pathlib import Path
from PIL import Image
import sys,json,hashlib,datetime,shutil
T=Path(__file__).resolve().parent
def rec(p):
 p=Path(p);return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def save(p,j):p.write_text(json.dumps(j,indent=2),encoding='utf-8')
id,source=sys.argv[1:3];source=Path(source);d=T/'repairs/edge-material-v8-20261012'/id
request=d/(sys.argv[3] if len(sys.argv)>3 else 'request.json')
assert id in ['NM1','NM2','NM3','WM1','WM2']
im=Image.open(source);assert im.format=='PNG' and im.size==(1254,1254)
n=d/'native.png';assert not n.exists();shutil.copyfile(source,n)
j={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'succeeded_pending_visual_qa','tool':'image_gen.imagegen','route':'builtin','originalOutput':rec(source),'native':rec(n),'actualSize':[1254,1254],'actualModel':None,'actualQuality':None,'resized':False,'request':rec(request),'preparation':rec(d/'preparation.json'),'authority':[rec('D:/work/image/AGENTS.md'),rec('D:/work/image/docs/IMAGE_MODEL_REQUIREMENT.md')]}
save(d/'receipt.json',j)
c=T/'continuation-round-20261013.json'
if c.exists():s=json.loads(c.read_text(encoding='utf-8'))
else:s={'resumedAt':j['createdAt'],'currentCoordinate':'r15_c14','firstActualNewOutput':rec(n),'firstOriginalOutput':rec(source),'actualModel':None,'route':'builtin','rule':'2026-10-13 existing builtin permitted; actual model metadata absent','newOutputs':[],'formalAccepted':False}
s['newOutputs'].append({'id':id,'native':rec(n),'receipt':rec(d/'receipt.json')});s['updatedAt']=j['createdAt'];s['status']='generated_pending_local_composition_and_visual_qa';save(c,s)
print(json.dumps({'id':id,'native':rec(n),'receipt':rec(d/'receipt.json')}))
