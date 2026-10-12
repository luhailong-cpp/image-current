import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
errors=[];nrefs=0;records=[]
for p in sorted((R/'native').glob('*.png.generation.json')):
 g=read(p);im=Path(g['file'])
 assert Image.open(im).size==(1254,1254)
 assert sha(im)==g['sha256']
 assert g['actualModel'] is None and g['actualQuality'] is None
 assert g['submittedParameters']=={'model':None,'quality':None}
 assert g['configSnapshot']['model']=='gpt-image-2.5-sunburst' and g['configSnapshot']['quality']=='max'
 for path,expected in [(g['prompt'],g['promptSha256']),(g['evidence']['request'],g['evidence']['requestSha256']),(g['evidence']['receipt'],g['evidence']['receiptSha256'])]:
  assert sha(path)==expected,(str(p),path)
 for ref in g['references']:
  nrefs+=1;assert sha(ref['path'])==ref['sha256'],ref['path'];assert ref.get('role')
 records.append({'file':str(im),'sha256':sha(im),'record':str(p),'dimensions':[1254,1254]})
save(R/'candidate/all-generation-audit.json',{'tile':'r11_c09','generatedNativeImages':len(records),'verifiedReferenceHashes':nrefs,'errors':errors,'records':records,'failedRequestWithNoImage':'p23-v1','formalAccepted':False})
q=read(R/'qa/internal-review.json');m=read(R/'candidate/manifest.json')
m['status']=q['status'];m['internalReview']=str(R/'qa/internal-review.json');m['internalGeometryAccepted']=False
save(R/'candidate/manifest.json',m)
sel=read(R/'selected-patches.json');sel['status']=q['status'];sel['formalAccepted']=False;save(R/'selected-patches.json',sel)
save(R/'progress.json',{'tile':'r11_c09','status':q['status'],'generatedNativeCount':len(records),'nativePatchImageCount':18,'nativeJointRepairImageCount':2,'selectedNativePatchCount':16,'complete4kCandidateCount':1,'formalAcceptedCount':0,'geometryBlockingIssues':['p32-p33 hull bottom about60-80px offset'],'colorPendingSeams':['p13-p23','p33-p43'],'failedRequestCount':1,'candidateSha256':m['candidateSha256'],'nextStep':q['nextAction'],'updatedAt':datetime.now(timezone.utc).isoformat()})
paths=[R/'layout-only/joint-p32-p33-native-crop.png',R/'native/joint-p32-p33-v1.png',R/'native/joint-p32-p33-v2.png']
canvas=Image.new('RGB',(1200,448),'#333333');d=ImageDraw.Draw(canvas)
for i,p in enumerate(paths):
 canvas.paste(Image.open(p).crop((430,360,830,790)),(i*400,18));d.text((i*400+3,3),['BEFORE','REJECTED v1','REJECTED v2'][i],fill='white')
canvas.save(R/'qa/joint-repair-attempts-native.png')
print(json.dumps({'nativeImageCount':len(records),'refHashes':nrefs,'selected':16,'candidateSha256':m['candidateSha256'],'formalAccepted':False,'remainingGeometryIssue':'p32-p33'},ensure_ascii=False))

