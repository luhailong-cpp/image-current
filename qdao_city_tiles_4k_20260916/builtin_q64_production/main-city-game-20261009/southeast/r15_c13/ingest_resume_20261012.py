from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,shutil,sys
T=Path(__file__).resolve().parent; R=T/'repairs-resume-20261012'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o): Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
name=sys.argv[1]; receipt=read(R/(name+'.receipt.json')); prep=read(R/(name+'.preparation.json'))
original=Path(receipt['originalOutputPath']); im=Image.open(original)
assert im.format=='PNG' and im.size==(1254,1254)
assert im.mode in ('RGB','RGBA')
if im.mode=='RGBA': assert im.getchannel('A').getextrema()==(255,255)
dest=R/(name+'-native.png'); assert not dest.exists(); shutil.copy2(original,dest)
assert sha(original)==sha(dest)
out={'id':name,'path':str(dest),'sha256':sha(dest),'size':list(im.size),'mode':im.mode,'receipt':{'path':str(R/(name+'.receipt.json')),'sha256':sha(R/(name+'.receipt.json'))},'preparation':{'path':str(R/(name+'.preparation.json')),'sha256':sha(R/(name+'.preparation.json'))},'originalOutputPath':str(original),'originalOutputSha256':sha(original),'generatedAt':receipt['generatedAt'],'actualModel':None,'actualQuality':None,'resized':False,'status':'saved_pending_visual_qa'}
write(R/(name+'.source.json'),out)
record=read(T/'production-resume-20261012.json'); record['status']='new_actual_output_saved_pending_local_qa'; record['newCalls']=record.get('newCalls',0)+1
record.setdefault('newOutputs',[]).append(out)
record['actualNativeCount']=record['actualNativeCountBefore']+len(record['newOutputs'])
if not record['firstNewOutput']: record['firstNewOutput']=out
record['updatedAt']=datetime.now(timezone.utc).isoformat(); write(T/'production-resume-20261012.json',record)
print(json.dumps(out,ensure_ascii=False,indent=2))
