from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
q=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sources={
'northwest':q/'repair-r09_c04-v1-candidate-4096.png',
'northeast':q/'repair-r09_c05-v3-candidate-4096.png',
'southwest':q/'preflight-r10_c04-v1-candidate-4096.png',
'southeastPartial':q/'capacity-gate-r10c05-rows123-native.png'}
imgs={k:Image.open(v).convert('RGB') for k,v in sources.items()}
for k,im in imgs.items():assert im.size==((4096,3072) if k=='southeastPartial' else (4096,4096))
outs=[]
for i,xa in enumerate([0,800,1600,2400,3196],1):
 box1=[xa,4096-345,xa+900,4096];box2=[xa,0,xa+900,345]
 im=Image.new('RGB',(900,690))
 im.paste(imgs['northwest'].crop(box1),(0,0));im.paste(imgs['southwest'].crop(box2),(0,345))
 p=q/f'capacity-gate-2x2-northwest-southwest-boundary-{i}-100pct.png';im.save(p)
 outs.append({'path':str(p),'sha256':sha(p),'size':list(im.size),'operation':'two exact integer crops with canonical hard boundary, no resize/blend','sources':[{'key':'northwest','sourceBox':box1,'destination':[0,0]},{'key':'southwest','sourceBox':box2,'destination':[0,345]}],'globalRasterBoundarySegment':[[12288+xa,36864],[12288+xa+900,36864]],'notAcceptedArtwork':True})
im=Image.new('RGB',(900,900))
corners=[('northwest',[3646,3646,4096,4096],(0,0)),('northeast',[0,3646,450,4096],(450,0)),('southwest',[3646,0,4096,450],(0,450)),('southeastPartial',[0,0,450,450],(450,450))]
for k,b,d in corners:im.paste(imgs[k].crop(b),d)
p=q/'capacity-gate-2x2-central-junction-100pct.png';im.save(p)
outs.append({'path':str(p),'sha256':sha(p),'size':list(im.size),'operation':'four canonical core corner integer crops, no resize or blend','sources':[{'key':k,'sourceBox':b,'destination':list(d)} for k,b,d in corners],'globalRasterBox':[15934,36414,16834,37314],'notAcceptedArtwork':True})
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'gateActive':True,'newArtRequests':0,'sources':{k:{'path':str(v),'sha256':sha(v),'dimensions':list(imgs[k].size)} for k,v in sources.items()},'outputs':outs,'scope':'Existing first 2x2 sample boundaries. Southeast has only 12/16 native slots, so this is not a complete 2x2 deliverable. No missing pixels are filled.'}
(q/'capacity-gate-2x2-root-boundary-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'outputs':[o['path'] for o in outs]}))

