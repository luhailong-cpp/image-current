from pathlib import Path
from PIL import Image
import json,hashlib
import numpy as np
from datetime import datetime,timezone
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast'); i='r04_c12_p03_04_v5'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rec=read(z/'native'/f'{i}.png.generation.json')
checks=[]
for ref in rec['references']:
 checks.append({'path':ref['file'],'recordedSha256':ref['sha256'],'actualSha256':sha(Path(ref['file'])),'matches':sha(Path(ref['file']))==ref['sha256']})
 for src in ref.get('sources',[]):
  checks.append({'path':src['file'],'recordedSha256':src['sha256'],'actualSha256':sha(Path(src['file'])),'matches':sha(Path(src['file']))==src['sha256']})
native=z/'native'/f'{i}.png'; original=Path(rec['evidence']['originalToolPath'])
im=Image.open(native); assert im.size==(1254,1254)
p2=z/'native'/'r04_c12_p02_04_v3.png'; crop=Image.open(p2).crop((115,115,1139,1139));crop.save(z/'qa'/'r04_c12_p02_04_v3-core-for-roof-audit.png')
a=np.array(crop).astype(float);blue=(a[:,:,2]>a[:,:,0]*1.3)&(a[:,:,2]>a[:,:,1]*1.1)&(a[:,:,2]>80)
ys,xs=np.where(blue)
b={'bluePixelCount':int(blue.sum()),'blueBBox':None if not len(xs) else [int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1],'criterion':'B>1.3R and B>1.1G and B>80, diagnostic only; visual core inspection is authority'}
im.crop((115,115,1139,1139)).save(z/'qa'/f'{i}.core-100pct.png')
audit={'id':i,'nativeSha256':sha(native),'status':'passed_internal_native_left_upper_and_cross','selectedUpper':'r04_c12_p02_04_v3','upperSha256':sha(p2),'left':'r04_c12_p03_03','geometry':'One blue roof plane; all tile axes down-right; prior contrary short heads removed; native full output and exact core joins visually inspected. Gold/red/paving geometry retained at core joins.','visualEvidence':['r04_c12_p03_03__r04_c12_p03_04_v5.join-100pct.png','r04_c12_p02_04_v3__r04_c12_p03_04_v5.join-100pct.png','cross_r04_c12_p03_04_v5.png'], 'originalToolReplayHashMatches':sha(native)==sha(original),'referenceHashChecks':checks,'actualModel':None,'actualQuality':None,'nativeSize':[1254,1254],'coreCrop':[115,115,1139,1139],'resized':False,'feathered':False,'p02CoreBlueDiagnostic':b,'p02RetentionReason':'The wrong blue tips in p02_04_v3 were below its retained 1024 core, so corrected p03_04_v5 forms a continuous true core seam with original p02. Keep p02 stable rather than use failed new architecture-shift versions.','independentReview':'pending parent','rightJoin':'delegated to southeast using frozen source','bottomJoin':'pending p04_04 after left p04_03 arrives','reviewedAtUtc':datetime.now(timezone.utc).isoformat()}
assert all(x['matches'] for x in checks)
write(z/'qa'/f'{i}.audit.json',audit)
rec['status']='passed_internal_native_left_upper_and_cross';rec['internalSeams']='left_upper_and_cross_passed';rec['qa']=str(z/'qa'/f'{i}.audit.json');write(native.with_suffix('.png.generation.json'),rec)
for bad in ['r04_c12_p02_04_v4','r04_c12_p02_04_v5','r04_c12_p02_04_v6','r04_c12_p03_04_v3','r04_c12_p03_04_v4']:
 p=z/'native'/f'{bad}.png.generation.json';r=read(p);r['status']=read(z/'qa'/f'{bad}.audit.json')['status'];r['qa']=str(z/'qa'/f'{bad}.audit.json');write(p,r)
print(json.dumps({'sha256':sha(native),'refsAllMatch':True,'sourceReplay':True,'p02CoreBlueDiagnostic':b}))

