from native_work import *
import os, time, sys
def save_progress(path, value):
 temp=path.with_suffix(path.suffix+'.refresh-tmp')
 write(temp,value)
 for attempt in range(5):
  try: os.replace(temp,path);return
  except OSError:
   if attempt==4:raise
   time.sleep(0.2)
def refresh():
 p=read(ZONE/'progress.json'); tiles={}; complete=[];passed=[];selected=set()
 for sp in sorted(ZONE.glob('selection-r??_c??.json')):
  tid=sp.stem.replace('selection-','');s=read(sp);ids=[v for row in s['cores'] for v in row if v];selected.update(ids);dp=ZONE/'tiles'/f'{tid}.png.derivation.json';d=read(dp) if dp.exists() else {}
  internal=str(d.get('internalReview','')).startswith('passed') or d.get('status')=='internal_candidate_passed'
  if tid=='r03_c14':
   a=ZONE/'qa/r03_c14-acceptance.json'
   if a.exists():
    ar=read(a);internal=('passed' in str(ar.get('internalReview','')) or ar.get('internalCandidateVisualPass') is True or str(ar.get('status','')).startswith('passed_internal'))
  tiles[tid]={'coreCoverage':len(ids),'repairOverlays':len(s.get('overlays',[])),'internalPassed':internal,'missingCores':16-len(ids)}
  if len(ids)==16 and dp.exists():complete.append(tid)
  if internal:passed.append(tid)
 for dp in sorted((ZONE/'tiles').glob('r??_c??.png.derivation.json')):
  tid=dp.name.split('.')[0]
  if tid in tiles:continue
  d=read(dp); count=len(d.get('sources',[]));internal=str(d.get('internalReview','')).startswith('passed')
  tiles[tid]={'coreCoverage':count,'repairOverlays':len(d.get('requiredOverlays',[])),'internalPassed':internal,'missingCores':16-count}
  if count==16:complete.append(tid)
  if internal:passed.append(tid)
  selected.update(s['id'] for s in d.get('sources',[]) if 'id' in s)
 records=[read(f) for f in (ZONE/'native').glob('*.png.generation.json')]
 usable=[r for r in records if r.get('status','').startswith(('usable_native','usable_seed'))]
 p.update(status='native_production_in_progress',updatedAtUtc=now(),generatedNativeCount=len(records),usableNativeCount=len(usable),usableCorePatchCount=sum('_cross_' not in r['id'] for r in usable),usableRepairOverlayCount=sum('_cross_' in r['id'] for r in usable),selectedCoreCoordinateCount=len(selected),fullyCovered4kCount=len(complete),internalPassed4kCount=len(passed),complete4kCount=len(passed),tileSummary=tiles,activeTiles=['r04_c12','r04_c13'],nextStep='Finish connected2x2 below r03_c12/r03_c13, validate shared4K edges, then continue adjacent assigned tiles.',inFlightStatus='parallel builtin native generation and QA',delegatedElsewhere=['r01_c13','r01_c14','r02_c13','r02_c14'],ownedRemainingTarget4kCount=45,formalAcceptedCount=0)
 p['activeTiles']=sorted(set(t for t,v in tiles.items() if not v['internalPassed'])|set(f.stem.replace('patch-plan-','') for f in ZONE.glob('patch-plan-r??_c??.json') if f.stem.replace('patch-plan-','') not in tiles))
 p['currentTile']=sys.argv[1] if len(sys.argv)>1 else p.get('currentTile','r04_c12')
 p['currentPatch']=sys.argv[2] if len(sys.argv)>2 else p.get('currentPatch')
 p['worldSize']=[57344,57344]
 p['nextStep']='Finish cross-tile jar color repair and connected2x2 validation; continue adjacent r03_c11 and r04_c14 native artwork.'
 save_progress(ZONE/'progress.json',p)
 h=read(ZONE/'handoff.json');h.update(updatedAtUtc=now(),status=p['status'],generatedNativeCount=len(records),fullyCovered4kCount=len(complete),internalPassed4kCount=len(passed),finishedInternalCandidates=['tiles/'+t+'.png' for t in passed],pixelCoveredCandidates=['tiles/'+t+'.png' for t in complete],activeTiles=p['activeTiles'],currentTile='r04_c12',currentPatch='r04_c12_p02_04_v2',inFlightStatus=p['inFlightStatus'],nextAction=p['nextStep'],delegatedElsewhere=p['delegatedElsewhere'],ownedRemainingTarget4kCount=45)
 h['currentTile']=p['currentTile'];h['currentPatch']=p['currentPatch'];h['activeTiles']=p['activeTiles']
 save_progress(ZONE/'handoff.json',h)
 print(json.dumps({'native':len(records),'pixelCovered':complete,'internalPassed':passed,'tiles':tiles}))
if __name__=='__main__':refresh()

