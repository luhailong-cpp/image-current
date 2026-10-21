"""Copy and record a native 1254 AI repair without selecting or modifying art."""
from pathlib import Path
from PIL import Image
import argparse,json,hashlib,shutil,datetime
B=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(__doc__);p.add_argument('--request',required=True);p.add_argument('--source',required=True);p.add_argument('--output',required=True);a=p.parse_args()
def path(v):
 x=Path(v);return x.resolve() if x.is_absolute() else (B/x).resolve()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
qpath=path(a.request);src=path(a.source);out=path(a.output)
assert qpath.is_relative_to(B) and out.is_relative_to(B/'repairs')
gpath=Path(str(out)+'.generation.json');assert not out.exists() and not gpath.exists()
q=json.loads(qpath.read_text(encoding='utf-8-sig'))
for ref in q['references']:assert sha(path(ref['path']))==ref['sha256']
im=Image.open(src);assert im.format=='PNG' and im.size==(1254,1254) and im.mode in ('RGB','RGBA')
if im.mode=='RGBA':assert im.getextrema()[3]==(255,255)
gb=q['globalNativeBox'];cb=q['globalCoreBox'];assert gb[2]-gb[0]==1254 and gb[3]-gb[1]==1254 and cb==[gb[0]+115,gb[1]+115,gb[2]-115,gb[3]-115]
shutil.copy2(src,out);assert sha(src)==sha(out)
r={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kind':'native-AI-seam-repair','repairId':q['repairId'],'file':str(out),'sha256':sha(out),'width':1254,'height':1254,'mode':im.mode,'sourceToolFile':str(src),'sourceToolSha256':sha(src),'request':{'path':str(qpath),'sha256':sha(qpath)},'coordinates':{k:q[k] for k in ['globalNativeBox','globalCoreBox','coreInNative']},'route':'builtin','actualModel':None,'actualQuality':None,'returnedResultKeys':['image_url','output_hint'],'nativePixelsResampled':False,'status':'native-repair-pending-overlay-qa','formalAccepted':False}
with gpath.open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'output':str(out),'sha256':sha(out),'record':str(gpath),'recordSha256':sha(gpath),'size':[1254,1254]}))
