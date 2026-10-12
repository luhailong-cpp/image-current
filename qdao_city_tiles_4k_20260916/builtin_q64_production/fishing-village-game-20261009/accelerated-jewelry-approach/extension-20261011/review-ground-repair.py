from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
b=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/accelerated-jewelry-approach');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
for v in range(1,7):
 d=b/'r05_c11/repairs'/f'ground-halo-v{v}'
 status='PASS_LOCAL_PROPOSAL' if v==6 else 'NOT_SELECTED_INTERMEDIATE'
 findings={'reviewedAt':datetime.now(timezone.utc).isoformat(),'status':status,'nativeScaleReview':True,'rawSha256':sha(d/'native-result.png'),'proposalSha256':sha(d/'proposal-native.png'),'selectedForCandidate':v==6,'findings':(['Former vertical ground boundary removed, diagonal grout continues, net shadow crosses former line naturally. Native mask band and ground junction visually inspected; bench and posts excluded from mask.'] if v==6 else ['Intermediate generation preserved; residual short vertical tonal artifact or changed lighting prevented selection. Final correction is ground-halo-v6.']),'formalAccepted':False}
 (d/'qa/findings.json').write_text(json.dumps(findings,indent=2)+'\n',encoding='utf-8')
 p=d/'proposal.json';r=read(p);r['status']=status;r['qa']=str(d/'qa/findings.json');p.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print('Ground repair v6 selected; five intermediate raws retained')

