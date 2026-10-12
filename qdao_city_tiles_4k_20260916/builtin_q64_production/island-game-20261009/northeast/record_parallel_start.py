from native_work import *
p=read(ZONE/'progress.json')
p.update(generatedNativeCount=len(list((ZONE/'native').glob('*.png.generation.json'))),status='parallel_native_generation',currentTile='r03_c13',currentPatch='r03_c13_p03_03',nextStep='Wait repaired p03_02 anchor then generate p03_03; native_column produces column2; provenance_audit produces r03_c14.',updatedAtUtc=now())
p['activeTiles']=['r03_c13','r03_c14'];write(ZONE/'progress.json',p)
h=read(ZONE/'handoff.json');h.update(currentPatch=p['currentPatch'],currentTile=p['currentTile'],nextAction=p['nextStep'],activeTiles=p['activeTiles'],updatedAtUtc=now());write(ZONE/'handoff.json',h)
t=read(ZONE/'tile-plan.json')
for x in t['tiles']:
 if x['id'] in p['activeTiles']: x['status']='native_generation_in_progress'
write(ZONE/'tile-plan.json',t)

