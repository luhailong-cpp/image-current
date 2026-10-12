from pathlib import Path
import json, hashlib
from datetime import datetime,timezone
from PIL import Image
T=Path(__file__).resolve().parent;D=T/'repair-batches/west-cap-material-01'
def ref(f):return {'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
def savej(f,v):
 assert not f.exists(),str(f)
 f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
req=json.loads((D/'request.json').read_text(encoding='utf-8'));native=D/'native.png';host=Path('C:/Users/luyua/.codex/generated_images/01a1345e-0afa-7220-8dcc-4eee714800d3/exec-99c806f6-4ba7-46dc-9ee6-8bb482868344.png')
assert ref(native)['sha256']==ref(host)['sha256']
savej(D/'generation.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'route':'builtin_image_gen','actualModel':None,'actualQuality':None,'sourceHostFile':str(host),'sourceNativeFile':ref(native),'request':ref(D/'request.json'),'parameters':ref(D/'parameters.json'),'worldBoxWithHalo':req['nativeWorldBox'],'tileOriginXY':req['tileOriginXY'],'hostByteIdentical':True,'formalAccepted':False})
base=Image.open(req['inputReferences'][0]['file']).convert('RGB');n=Image.open(native).convert('RGB');assert n.size==(1254,1254)
roi=[200,540,410,653];cr=[0,1052,210,1165];base.paste(n.crop(roi),cr[:2]);base.save(D/'trial-candidate-4096.png')
w=Image.open(req['inputReferences'][1]['file']).convert('RGB');detail=Image.new('RGB',(540,380));detail.paste(w.crop((3976,1000,4096,1380)),(0,0));detail.paste(base.crop((0,1000,420,1380)),(120,0));detail.save(D/'trial-detail-native.png')
savej(D/'trial.json',{'sourceROI':roi,'candidateROI':cr,'candidate':ref(D/'trial-candidate-4096.png'),'native':ref(native),'generationRecord':ref(D/'generation.json'),'nativeWorldBox':req['nativeWorldBox'],'exactSameWorldNativePixels':True,'sourceResampled':False,'blended':False,'formalAccepted':False,'status':'pending_visual_review'})
