from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
import numpy as np
from PIL import Image
W=Path(__file__).resolve().parent;B=W.parents[1];sys.path.insert(0,str(B/'work-r03_c04'));sys.path.insert(0,str(B))
from apply_r03_c04_repairs import overlay_mask
rd=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:np.asarray(Image.open(p).convert('RGB')).copy()
m=rd(W/'stage-north/assembly.json');a=rgb(m['candidate']['file']);ids=np.asarray(Image.open(m['sourceIdMap']['file'])).copy();r=rgb(W/'r03_c04_road_edge_west_v03.png');rec=rd(W/'r03_c04_road_edge_west_v03.png.generation.json');box=rec['globalNativeBox'];x,y=box[0]-12288,box[1]-8192;region=a[y:y+1254,x:x+1254]
mask,dp=overlay_mask(region,r);region[mask]=r[mask];sid=max(s['sourceId'] for s in m['sources'])+1;ids[y:y+1254,x:x+1254][mask]=sid
D=W/'west-mechanical-diagnostic';D.mkdir(exist_ok=True)
Image.fromarray(a).save(D/'r03_c04.candidate.png');Image.fromarray(ids).save(D/'r03_c04.source-id.png')
for name,bb in [('top',(14400,10860,15900,11200)),('left',(14400,10975,14800,12229)),('right',(15550,10975,16000,12229)),('bottom',(14530,11980,15784,12288)),('whole-road',(14530,11200,16384,12288))]:
 x0,y0,x1,y1=bb;Image.fromarray(a[y0-8192:y1-8192,x0-12288:x1-12288]).save(D/(name+'.100pct.png'))
sources=m['sources']+[{'sourceId':sid,'file':str(W/'r03_c04_road_edge_west_v03.png'),'sha256':rec['sha256'],'generationRecord':str(W/'r03_c04_road_edge_west_v03.png.generation.json'),'generationRecordSha256':sha(W/'r03_c04_road_edge_west_v03.png.generation.json'),'globalNativeBox':box,'actualModel':None,'actualQuality':None}]
proof=[]
for s in sources:
 yy,xx=np.nonzero(ids==s['sourceId'])
 if not len(xx):continue
 v=rgb(s['file']);sx=xx+12288-s['globalNativeBox'][0];sy=yy+8192-s['globalNativeBox'][1];assert np.array_equal(a[yy,xx],v[sy,sx]);proof.append({'sourceId':s['sourceId'],'pixels':len(xx),'mismatches':0})
data={'createdAt':datetime.now(timezone.utc).isoformat(),'status':'mechanical-diagnostic-not-approved','candidate':{'file':str(D/'r03_c04.candidate.png'),'sha256':sha(D/'r03_c04.candidate.png')},'sourceIdMap':{'file':str(D/'r03_c04.source-id.png'),'sha256':sha(D/'r03_c04.source-id.png')},'sources':sources,'path':dp,'formalAccepted':False,'proof':{'pixels':16777216,'mismatches':0,'contributions':proof},'baseAssembly':str(W/'stage-north/assembly.json')}
(D/'assembly.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8');print(json.dumps({'candidate':data['candidate'],'pixels':int(mask.sum())}))
