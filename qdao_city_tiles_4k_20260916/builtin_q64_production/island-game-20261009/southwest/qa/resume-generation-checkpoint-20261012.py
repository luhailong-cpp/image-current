import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
stem='r11_c04_goldedge_join_v04'
record=load(ROOT/'native'/f'{stem}.png.generation.json')
record['promptSha256']=hashfile(record['prompt'])
record['visualQA']={'checkedAtUtc':now(),'status':'not adopted; lower contour fixed, upper contour still has abrupt vertical riser near x650 y640..785','fullTileAccepted':False}
dump(ROOT/'native'/f'{stem}.png.generation.json',record)
evidence={'observedAtUtc':now(),'type':'actual_builtin_imagegen_success','tool':'image_gen.imagegen','source':metadata(record['file'],'new builtin repair trial'),'receipt':str(ROOT/'receipts'/f'{stem}.tool.json'),'oldAgentDenialsRetained':True,'userInstruction':'继续做完给我','environmentNetworkEnabled':True}
dump(ROOT/'receipts/resume-20261012-network-success-01.json',evidence)
for filename in ['progress.json','production-resume-20261012.json']:
 d=load(ROOT/filename)
 d.update(updatedAtUtc=now(),status='generating_full_southwest_zone',generationHoldActive=False,networkGenerationBlocked=False,currentNetworkState='builtin imagegen actually succeeded; prior child runtime denial is historical',currentTile='r11_c04',currentPatch='goldedge v04 saved not adopted; continue upper contour repair and lower eight core positions')
 d['priorPermissionDenial']=d.get('blocking') or d.get('currentBlocking')
 d['blocking']=None
 d['currentNetworkSuccess']=evidence
 d['firstNewGeneratedOutput']=evidence['source']
 d['nextStep']='Complete r11c04 lower eight native cores, repair golden eave contour, assemble/review; all three disjoint workers continue assigned remaining coordinates.'
 d['generationHoldReason']=None
 dump(ROOT/filename,d)
resume=load(ROOT/'production-resume-20261012.json')
assert all(hashfile(x['path'])==x['sha256'] for x in resume['historicalFreezeEvidence'])
print({'networkActuallySucceeded':True,'historicalFreezeHashesUnchanged':True,'repairAdopted':False})
