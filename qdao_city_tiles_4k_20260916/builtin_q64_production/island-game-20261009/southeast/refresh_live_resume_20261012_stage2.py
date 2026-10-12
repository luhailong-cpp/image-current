"""Refresh current resumable state without modifying historical freeze or upload snapshot."""
from workflow import *
from pathlib import Path
import sys
expected='fde0f73f4342364e2d75c54401e9d4b66e378d3583d86ed6b2e3c13368954eeb'
assert sha(ROOT/'migration-freeze-20261011.json')==expected
r=read(ROOT/'production-resume-20261012.json')
r['counts']['generatedNativeCount']=len(list((ROOT/'native').glob('*.png')))
r.update(updatedAtUtc=now(),status='active_builtin_native_continuation',inFlightRequests=['r12_c12_lower_deck_joint_v01','r12_c12_p34_v01'])
r['savedRepairUnderReview']=None
r['savedRepairReview']='qa/r12-c12-saved-deck-resume-20261012-v02/root-visual-review.json'
r['pendingRepairs']=[{'object':'p41/p42 long floorboards','status':'whole-object builtin native repair in flight'}]
r['nextStep']='Generate missing p34/p44, inspect whole lower board joint, then exact full 4K source proof and true internal seams.'
write(ROOT/'production-resume-20261012.json',r)
p=read(ROOT/'progress.json')
p.update(updatedAt=now(),generatedNativeCount=r['counts']['generatedNativeCount'],remainingAssigned4kCount=49-p['fullyCovered4kCount'],nextStep=r['nextStep'],rootInFlightCount=2,inFlight=True,latestNewOutput={'file':str(ROOT/'native/r12_c12_p43_v01.png'),'sha256':sha(ROOT/'native/r12_c12_p43_v01.png')})
write(ROOT/'progress.json',p)
p=read(ROOT/'progress-r12_c12.json')
p['workingVersions'].update({'24':'v03','42':'v01','43':'v01'})
p['generatedNativeCount']=len(list((ROOT/'native').glob('r12_c12*.png')))
p['missingPatches']=['r12_c12_p34','r12_c12_p44']
p['pendingRepairs']=[{'object':'p41/p42 floor joint','status':'whole-object native generation in flight'}]
p.update(updatedAt=now(),inFlight=True,inFlightRequests=r['inFlightRequests'],status='active_native_continuation',nextStep=r['nextStep'])
write(ROOT/'progress-r12_c12.json',p)
assert sha(ROOT/'migration-freeze-20261011.json')==expected
print(json.dumps({'native':r['counts']['generatedNativeCount'],'full4k':p['fullyCovered4kCount'],'globalFull4k':r['counts']['fullyCovered4kCount'],'missing':p['missingPatches']}))
