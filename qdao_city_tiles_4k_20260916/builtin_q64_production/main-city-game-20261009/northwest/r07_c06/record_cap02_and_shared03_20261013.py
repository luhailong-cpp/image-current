from pathlib import Path
import json,hashlib
from PIL import Image
from datetime import datetime,timezone
T=Path(__file__).resolve().parent;B=T/'repair-batches/west-cap-material-02';S=T.parent/'r07_c05/bridges/shared-east-lower-03';Q=T/'qa/restart-integration-20261013'
def ref(f):return {'file':str(f),'sha256':hashlib.sha256(Path(f).read_bytes()).hexdigest()}
def wj(f,v):
 assert not f.exists(),str(f)
 f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
host=Path('C:/Users/luyua/.codex/generated_images/01a1345e-0afa-7220-8dcc-4eee714800d3/exec-6c6cdd96-2d55-4616-9d9b-19ebe684c11c.png');assert ref(host)['sha256']==ref(B/'native.png')['sha256'];req=json.loads((B/'request.json').read_text(encoding='utf-8'))
wj(B/'generation.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'route':'builtin_image_gen','actualModel':None,'actualQuality':None,'sourceHostFile':str(host),'file':ref(B/'native.png'),'request':ref(B/'request.json'),'parameters':ref(B/'parameters.json'),'worldBox':req['nativeWorldBox'],'tileOriginXY':[-200,512],'nativePixels':[1254,1254],'hostByteIdentical':True,'status':'candidate_not_adopted','formalAccepted':False})
c=Image.open(T/'candidate/r07_c06-candidate-native-roi-v08.png');n=Image.open(B/'native.png');sr=[200,455,450,680];tr=[0,967,250,1192];c.paste(n.crop(sr),tr[:2]);c.save(B/'trial-expanded-cap-4096.png');w=Image.open(T.parent/'r07_c05/candidate/r07_c05-candidate-native-rois-final-872df04172946ceb/candidate.png');d=Image.new('RGB',(550,420));d.paste(w.crop((3976,900,4096,1320)),(0,0));d.paste(c.crop((0,900,430,1320)),(120,0));d.save(B/'trial-expanded-cap-detail.png');wj(B/'trial.json',{'candidate':ref(B/'trial-expanded-cap-4096.png'),'sourceROI':sr,'tileROI':tr,'native':ref(B/'native.png'),'status':'pending_review','formalAccepted':False})
wj(Q/'shared-bottom-independent-review.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'/root/finish_r07_c06','source':ref(S/'native.png'),'trial':ref(S/'trial-bottom-only.json'),'actuallyViewed':[dict(**ref(S/f),viewDetail='original',verdict='passed_local_scope') for f in ['trial-bottom-detail.png','trial-top-perimeter.png','trial-bottom-perimeter.png','trial-left-perimeter.png','trial-right-perimeter.png']],'finding':'Vertical grout segment joins upper and lower diagonal endpoints. Four perimeter strips preserve continuous grout and grain. Only bottom ROI approved; other mixed-output areas explicitly excluded.','approvedRightSourceROI':[627,795,657,910],'approvedRightTileROI':[0,2995,30,3110],'formalAccepted':False})
