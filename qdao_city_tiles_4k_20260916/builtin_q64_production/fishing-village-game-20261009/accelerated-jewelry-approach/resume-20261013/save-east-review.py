from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
b=Path(__file__).resolve().parents[1];d=b/'resume-20261013/east-r05-c11-c12'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=read(d/'manifest.json');assert all(sha(x['file'])==x['sha256'] for x in m['files'])
assert sha(m['own']['file'])==m['own']['sha256'] and sha(m['neighbor']['file'])==m['neighbor']['sha256']
segments=[]
for row in m['files']:
 name=Path(row['file']).name
 if name in ['east-r1.png','east-r2.png'] or name.startswith('roof-context-'):
  verdict='PENDING_NEIGHBOR_ROOF_REPAIR';finding='Roof tile geometry joins, but the smaller right-side blue tiles have sharply segmented bright checker highlights and a tone/paint transition at the boundary. Current neighbor progress already identifies its west roof highlight repair as pending.'
 else:
  verdict='PASS';finding='Timber, plaster frame, red wall, stone, fish and crate geometry join without an actionable own-side discontinuity in the viewed native strip.'
 segments.append(dict(row,status=verdict,reviewMethod='Root viewed original1:1 native pixels',finding=finding))
out={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'status':'EXTERIOR_PAIR_PENDING_NEIGHBOR_REPAIR','scope':'One current exterior pair r05_c11 east / r05_c12 west; four native seam strips plus three native roof contexts.','own':m['own'],'neighbor':m['neighbor'],'segments':segments,'blockingFindings':[{'issue':'Blue roof highlight/tone continuity across lower roof','boundary':'r05_c11 east / r05_c12 west','primaryRepairSide':'r05_c12 neighbor side, already owned and listed pending in neighbor progress','ownSideRepairRequiredAtThisCheckpoint':False,'evidenceFiles':[str(d/'east-r2.png'),str(d/'roof-context-y512.png'),str(d/'roof-context-y1024.png')]}],'ownPendingRepairs':[],'formalAccepted':False,'exteriorPairPassed':False,'nativePixelsResized':False,'newImageCalls':0,'existingImagesMutated':False,'nextAction':'Re-review the native exterior seam after neighbor owner saves its roof repair. Preserve assigned left-side artwork.','independentReview':'pending'}
write(d/'root-findings.json',out)
print(json.dumps({'status':out['status'],'ownRepairCount':0,'formalAccepted':False,'ownImageUnchanged':True}))
