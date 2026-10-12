from workflow import *
from PIL import Image
import numpy as np
versions={'r08_c12':'v15','r09_c11':'v05','r09_c12':'v09','r09_c13':'v02','r10_c11':'v04','r10_c12':'v02','r10_c13':'v02','r11_c11':'v02','r11_c12':'v02','r11_c13':'v02'}
tiles=[]
for tid,v in versions.items():
 f=ROOT/'tiles'/f'{tid}.candidate-{v}.png';assert f.exists()
 tiles.append({'tile':tid,'candidate':str(f),'sha256':sha(f),'fullyCovered':True,'internalPassed':True,'externalPassed':tid=='r10_c12','localArtworkAcceptanceReady':tid=='r10_c12','formalAccepted':False,'pending':'main coordinator final acceptance' if tid=='r10_c12' else 'remaining external neighbor edges'})
native=list((ROOT/'native').glob('*.png'));latest=max(native,key=lambda p:p.stat().st_mtime)
counts={'generatedNativeCount':len(native),'fullyCovered4kCount':len(tiles),'complete4kCount':len(tiles),'internalPassed4kCount':sum(x['internalPassed'] for x in tiles),'externalPassed4kCount':1,'localArtworkAcceptanceReadyCount':1,'formalAcceptedCount':0}
state=read(ROOT/'production-state.json');state.update(updatedAt=now(),status='active_contiguous_neighborhood_closure',counts=counts,tiles=tiles,activeWorkers={'root':'r12_c12 dock native continuation','coordinate_audit':'r08c11 northern adjacent tile; roof promoted and passed','left_continue':'r12c11 dock continuation','right_continue':'r12c13 dock and water continuation'},latestSuccessfulNative=str(latest),latestSuccessfulNativeSha256=sha(latest),latestSuccessfulNativeStatus='native received; use each tile review manifest for acceptance',nextStep='Finish adjacent r12 row and r08c11 with original-scale internal and neighbor joins, then close remaining neighborhood borders.')
write(ROOT/'production-state.json',state)
p=read(ROOT/'progress.json');p.update(counts);p.update(updatedAt=now(),status=state['status'],currentTile='r12_c12',currentPatch='native continuation',nextStep=state['nextStep'],coveredTiles=list(versions),rootTilesCovered=list(versions),internalPassedTiles=[t['tile'] for t in tiles if t['internalPassed']],latestCandidates={t['tile']:t['candidate'] for t in tiles},unreviewedCandidateRevision=None,lastError=None);write(ROOT/'progress.json',p)
round=read(ROOT/'continuation-round-20261011.json');round.update(counts);round.update(updatedAt=now(),status='active_builtin_native_continuation',currentCoordinate='r12_c12',latestActualOutput={'file':str(latest),'sha256':sha(latest)},nextStep=state['nextStep'],latestMergedCandidates={t['tile']:t['candidate'] for t in tiles},remainingDefect='r12c12 has ungenerated cores and active board/post junction repairs; promoted roof passed with documented minor groove phase');write(ROOT/'continuation-round-20261011.json',round)
write(ROOT/'migration-production-handoff-20261011.json',{'updatedAt':now(),'scope':'southeast production artifacts only','gitActionsOwnedByThisChat':False,'centralizedGitMigrationAcknowledged':True,'counts':counts,'productionState':'production-state.json','latestCandidates':tiles,'latestNative':{'file':str(latest),'sha256':sha(latest)},'neverDeleteUniqueNativeOrWIP':True})
print(json.dumps({'counts':counts,'latestNative':latest.name}))
