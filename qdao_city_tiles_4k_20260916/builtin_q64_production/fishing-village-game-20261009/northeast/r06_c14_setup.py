from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
src=(z/'r06_c13_extension.py').read_text(encoding='utf-8')
src=src.replace("from PIL import Image","from PIL import Image,ImageOps")
src=src.replace("T='r06_c13';ORIGIN=(49152,20480)","T='r06_c14';ORIGIN=(53248,20480)")
src=src.replace("LEFT=['r06_c12_p14-p13-bridge-p14-candidate.png','r06_c12_p24-v2.png','resume-20261010-stall-upper-v1.png','resume-20261010-stall-lower-v1.png']","LEFT=['r06_c13_p14-v1.png','r06_c13_p24-v1.png','r06_c13_p34-v1.png','r06_c13_p44-v1.png']")
src=src.replace("'tileCoreBox':[49152,20480,53248,24576]","'tileCoreBox':[53248,20480,57344,24576]")
src=src.replace("box=[1040,412,1190,565]","box=[1100,420,1254,566]").replace("(1200,1224)","(1232,1168)")
src=src.replace("co=coords(p);im=Image.open(C['layoutReference']).convert('RGB').transform((N,N),Image.Transform.EXTENT,co['overviewBox'],Image.Resampling.BICUBIC)","co=coords(p);layout=Image.open(C['layoutReference']).convert('RGB');pad=Image.new('RGB',(layout.width+8,layout.height));pad.paste(layout,(0,0));pad.paste(layout.crop((layout.width-1,0,layout.width,layout.height)).resize((8,layout.height)),(layout.width,0));im=pad.transform((N,N),Image.Transform.EXTENT,co['overviewBox'],Image.Resampling.BICUBIC)")
src=src.replace(",ref(Z/'guides'/f'{T}.context-layout-only.png','wider context layout only')","")
dst=z/'r06_c14_extension.py'
assert not dst.exists()
dst.write_text(src,encoding='utf-8')
host=Path(r'C:/Users/luyua/.codex/generated_images/01a12561-477e-77c1-aabe-f981f8b424eb')
records=[json.loads(p.read_text(encoding='utf-8-sig')) for p in (z/'native').glob('*.generation.json')]
hostaudit=[]
for p in sorted(host.glob('*.png'),key=lambda x:x.stat().st_mtime,reverse=True)[:8]:
 h=hashlib.sha256(p.read_bytes()).hexdigest()
 matches=[r.get('file') for r in records if r.get('sha256')==h]
 hostaudit.append({'sourceHost':str(p),'sha256':h,'alreadyArchivedMatches':matches})
audit={'tile':'r06_c14','observedAtUtc':datetime.now(timezone.utc).isoformat(),'interruptionAudit':hostaudit,'existingC14NativeCount':0,'unarchivedSuccessfulC14OutputsFound':False,'resumedBuiltinRequest': 'pending','actualModel':None,'actualQuality':None,'networkAuthorization':'Parent relayed user permission restored and continue; one normal builtin continuation, stop after permission/network refusal','missingCoordinates':[f'r06_c14_p{r}{c}' for c in range(1,5) for r in range(1,5)],'formalAccepted':False}
(z/'records/r06_c14.local-continuation-20261011.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'helper':str(dst),'hostOutputsAudited':len(hostaudit),'allRecentHostOutputsAlreadyArchived':all(x['alreadyArchivedMatches'] for x in hostaudit)}))

