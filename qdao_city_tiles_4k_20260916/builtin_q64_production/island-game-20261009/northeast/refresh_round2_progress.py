from native_work import *
import re, collections, shutil
stamp=now()
passed=[];complete=[];summary={}
selections={f.stem.replace('selection-',''):read(f) for f in sorted(ZONE.glob('selection-r??_c??.json'))}
selected=[]
for tid,s in selections.items():
 ids=[v for row in s['cores'] for v in row if v]; selected+=ids
 dp=ZONE/'tiles'/f'{tid}.png.derivation.json'; d=read(dp) if dp.exists() else {}
 internal=str(d.get('internalReview','')).startswith('passed')
 if len(ids)==16 and dp.exists():complete.append(tid)
 if internal and len(ids)==16:passed.append(tid)
 summary[tid]={'coreCoverage':len(ids),'missingCores':16-len(ids),'repairOverlays':len(s.get('overlays',[])),'internalPassed':internal,'candidateFile':str(ZONE/'tiles'/f'{tid}.png') if tid in complete else None,'sha256':d.get('sha256'),'pendingIssues':s.get('pendingIssues',[])}
records=[read(f) for f in (ZONE/'native').glob('*.png.generation.json')]
bases=set()
for r in records:
 m=re.fullmatch(r'(r\d{2}_c\d{2}_p\d{2}_\d{2})(?:_v\d+)?',r['id'])
 if m:bases.add(m.group(1))
excluded={'r01_c13','r01_c14','r02_c13','r02_c14'}
inventory=[]
for tr in range(1,8):
 for tc in range(8,15):
  tid=f'r{tr:02d}_c{tc:02d}'
  if tid in excluded:continue
  coords=[f'{tid}_p{r:02d}_{c:02d}' for r in range(1,5) for c in range(1,5)]
  s=selections.get(tid,{'cores':[[None]*4 for _ in range(4)]})
  ids=[v for row in s['cores'] for v in row if v]
  chosen={re.sub(r'_v\d+$','',v) for v in ids}
  inventory.append({'tileId':tid,'completeNativeCoverage':tid in complete,'internalPassed':tid in passed,'formalAccepted':False,'selectedCoreIds':ids,'missingGeneratedCoordinates':[v for v in coords if v not in bases],'unselectedCoordinates':[v for v in coords if v not in chosen],'pendingIssues':s.get('pendingIssues',[])})
inventory_path=ZONE/'qa/continuation-inventory-round2-20261011.json'
write(inventory_path,{'updatedAtUtc':stamp,'ownedTileCount':45,'targetCoreCoordinates':720,'generatedNativeFiles':len(records),'uniqueGeneratedCoreCoordinates':len(bases),'selectedCoreCoordinates':len(selected),'missingGeneratedCoreCoordinates':720-len(bases),'missingSelectedCoreCoordinates':720-len(selected),'fullCoverageTiles':len(complete),'internallyPassedTiles':len(passed),'formalAcceptedTiles':0,'excludedElsewhere':sorted(excluded),'tileInventory':inventory})
first=read(ZONE/'qa/builtin-resumed-round2-20261011.json')
p=read(ZONE/'progress.json')
for e in p.get('errors',[]):
 if not e.get('resolved',False) and 'network permission was revoked' in e.get('error',''):
  e.update(resolved=True,resolvedAtUtc=first['generatedAtUtc'],resolutionEvidence=str(ZONE/'qa/builtin-resumed-round2-20261011.json'))
p.update(status='native_production_resumed',updatedAtUtc=stamp,generatedNativeCount=len(records),
 selectedCoreCoordinateCount=len(selected),generatedCoreCoordinateCount=len(bases),
 fullyCovered4kCount=len(complete),internalPassed4kCount=len(passed),complete4kCount=len(passed),
 missingFullCoverage4kCount=45-len(complete),formalAcceptedCount=0,
 currentTile='r05_c12',currentPatch='parallel adjacent native generation and QA',
 activeTiles=[t for t in summary if t not in passed],tileSummary=summary,
 nextStep='Complete adjacent r03_c11, r05_c12, r05_c13 and their shared edges; continue remaining owned tiles.',
 inFlightStatus='builtin native generation and visual QA active',networkBlockResolved=True,
 deliveryIndex=str(ZONE/'exports/20261011-local-v2/delivery-index.json'),firstRealNewOutputThisRound=first)
usable=[r for r in records if r.get('status','').startswith(('usable_native','usable_seed'))]
p.update(usableNativeCount=len(usable),usableCorePatchCount=sum('_cross_' not in r['id'] for r in usable),usableRepairOverlayCount=sum('_cross_' in r['id'] for r in usable))
p.pop('nextSteps',None)
p['continuationInventory']=inventory_path.as_posix()
write(ZONE/'progress.json',p)
h=read(ZONE/'handoff.json')
h.update(status=p['status'],updatedAtUtc=stamp,generatedNativeCount=len(records),
 fullyCovered4kCount=len(complete),internalPassed4kCount=len(passed),selectedCoreCoordinateCount=len(selected),
 generatedCoreCoordinateCount=len(bases),missingFullCoverage4kCount=45-len(complete),
 activeTiles=p['activeTiles'],currentTile=p['currentTile'],currentPatch=p['currentPatch'],
 inFlightStatus=p['inFlightStatus'],nextAction=p['nextStep'],networkBlockResolved=True,
 finishedInternalCandidates=['tiles/'+t+'.png' for t in passed],pixelCoveredCandidates=['tiles/'+t+'.png' for t in complete],
 deliveryIndex=p['deliveryIndex'],firstRealNewOutputThisRound=first)
h.pop('nextSteps',None)
h['continuationInventory']=inventory_path.as_posix()
write(ZONE/'handoff.json',h)
cp=ZONE/'continuation-round-20261011.json'; previous=read(cp)
history=ZONE/'qa/history/continuation-before-round2-20261011.json'
if not history.exists():write(history,previous)
current={'resumedAt':first['generatedAtUtc'],'updatedAtUtc':stamp,'status':p['status'],
 'currentCoordinate':p['currentPatch'],'firstRealNewImageOutput':first,
 'firstRealNewImageOutputSha256':first['sha256'],'networkBlockResolved':True,
 'generatedNativeFiles':len(records),'generatedCoreCoordinates':len(bases),'selectedCoreCoordinates':len(selected),
 'ownedTargetTiles':45,'completeNativeCoverageTiles':len(complete),'internalPassedTiles':passed,
 'formalAcceptedTiles':0,'missingFullCoverageTiles':45-len(complete),
 'tileSummary':summary,'deliveryIndex':p['deliveryIndex'],'inventory':inventory_path.as_posix(),
 'resolvedInternalColorRepairs':str(ZONE/'qa/color-repairs-20261011-merge.json'),
 'nextStep':p['nextStep'],'previousRound':history.as_posix(),
 'actualModel':None,'actualQuality':None,'submittedModel':None,'submittedQuality':None}
write(cp,current)
print(json.dumps({'native':len(records),'coordinates':len(bases),'selected':len(selected),'full':complete,'passed':passed,'active':p['activeTiles']}))

