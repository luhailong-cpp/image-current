from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parent.parent
rd=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
RJ=R/'work-r03_c04/joint-south-resume/proposal-v1'
SC=R/'work-r04_c04/joint-west/final-v3'
spec=[('r03_c03',D/'r03_c03.joint-proposal.png',D/'r03_c03.source-id.png',D/'joint-assembly.json',[8192,8192],(3584,3584,4096,4096)),('r03_c04',RJ/'r03_c04.joint-proposal.png',RJ/'r03_c04.source-id.png',RJ/'joint-assembly.json',[12288,8192],(0,3584,512,4096)),('r04_c03',SC/'r04_c03.joint-proposal.png',SC/'r04_c03.source-id.png',SC/'joint-assembly.json',[8192,12288],(3584,0,4096,512)),('r04_c04',RJ/'r04_c04.joint-proposal.png',RJ/'r04_c04.source-id.png',RJ/'joint-assembly.json',[12288,12288],(0,0,512,512))]
result={'createdAt':datetime.now(timezone.utc).isoformat(),'status':'diagnostic-before-right-column-paving-rebase','formalAccepted':False,'globalBox':[11776,11776,12800,12800],'nativeScale':1,'inputs':[],'mismatchedPixels':0,'pixelsVerified':0}
pieces=[]
for tile,p,ip,mp,origin,box in spec:
    m=rd(mp);a=np.asarray(Image.open(p).convert('RGB').crop(box));i=np.asarray(Image.open(ip).crop(box));sources={s.get('jointSourceId',s.get('sourceId')):s for s in m['sources']}
    for key in np.unique(i):
        s=sources[int(key)];assert sha(s['file'])==s['sha256'];v=np.asarray(Image.open(s['file']).convert('RGB')); yy,xx=np.nonzero(i==key);bx,by,_,_=s['globalNativeBox'];sx=xx+origin[0]+box[0]-bx;sy=yy+origin[1]+box[1]-by; assert np.array_equal(a[yy,xx],v[sy,sx])
    result['inputs'].append({'tile':tile,'file':str(p),'sha256':sha(p),'sourceIdFile':str(ip),'sourceIdSHA256':sha(ip),'assembly':str(mp),'assemblySHA256':sha(mp),'crop':box})
    pieces.append(a);result['pixelsVerified']+=a.shape[0]*a.shape[1]
out=np.concatenate([np.concatenate(pieces[:2],axis=1),np.concatenate(pieces[2:],axis=1)],axis=0)
p=D/'center-current-four-quadrants.100pct.png';Image.fromarray(out).save(p);result['diagnostic']={'file':str(p),'sha256':sha(p)}
(D/'center-current-mechanical-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result['diagnostic']))
