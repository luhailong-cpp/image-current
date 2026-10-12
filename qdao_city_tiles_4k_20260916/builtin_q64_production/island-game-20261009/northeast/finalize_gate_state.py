from native_work import *
# Existing-only shared edge result; no acceptance of incomplete tiles.
p=ZONE/'qa/r03_c13__r03_c14.existing-border.json';q=read(p);q.update(status='passed_shared4096edge_visual_only',reviewedAtUtc=now(),reviewer='root',notes='All four exact native scale edge segments inspected. Water and fish fin/scales/stone paving continuous across shared line. Right tile remains incomplete with internal caustic repairs pending; no formal tile acceptance.');write(p,q)
# Refresh inventory while preserving original receipt time.
p=ZONE/'capacity-gate-ack.json';ack=read(p)
ack['workerInFlightStatus']={'native_column':'none; r04_c12 first request failed with missing approved style reference; no native output','provenance_audit':'none; r03_c14_p04_01 saved with full provenance; p04_02 failed before output due missing approved style reference'}
ack.update(inFlightStatus='none across root and all internal workers',confirmedAtUtc=now(),nativeOutputsPreserved=True,generatedNativeCount=len(list((ZONE/'native').glob('*.png'))),missingSharedInputs=['D:/work/image/config/image-generation.json','D:/work/image/designs/mail-ui-v1/01-mail-event.png'])
ack['auditOutputs']=['qa/r03_c13-provenance-audit.json','qa/r03_c14-capacity-gate-provenance-audit.json','capacity-road-building-risks.json','qa/r03_c14-capacity-risk-inventory.json']
write(p,ack)
records=[read(p) for p in (ZONE/'native').glob('*.png.generation.json')]
usable=[q for q in records if q.get('status','').startswith(('usable_native','usable_seed'))]
p=ZONE/'progress.json';s=read(p)
s.update(status='held_capacity_layout_validation_existing_QA_complete',updatedAtUtc=now(),generatedNativeCount=len(records),selectedCoreCoordinateCount=45,usableNativeCount=len(usable),usableCorePatchCount=sum('_cross_' not in q['id'] for q in usable),usableRepairOverlayCount=sum('_cross_' in q['id'] for q in usable),complete4kCount=1,complete4kCountDefinition='legacy field: internally passed candidate count; see fullyCovered4kCount for pixel coverage',fullyCovered4kCount=2,internalPassed4kCount=1,externalPassed4kCount=0,formalAcceptedCount=0,target4kCount=49,currentTile='r03_c13',currentPatch='r03_c13_p04_03_v2',activeTiles=['r03_c13','r03_c14'],inFlightStatus='none',nextStep='Await delegating-root capacity gate release and approved reference/config resolution; then redraw whole interrupted terrace joint and close contiguous2x2 with r04_c12/r04_c13 before continuing remaining49tile scope.',capacity5000Validated=False,worldSize=None)
s['tileSummary']={'r03_c12':{'coreCoverage':16,'repairOverlays':3,'internalPassed':True},'r03_c13':{'coreCoverage':16,'repairOverlays':1,'internalPassed':False,'issue':'terrace-front edge height discontinuity'},'r03_c14':{'coreCoverage':13,'repairOverlays':2,'internalPassed':False,'missingCores':3,'pendingJointRepairs':2},'r04_c12':{'coreCoverage':0,'status':'prepared only; no native image'}}
write(p,s)
p=ZONE/'handoff.json';h=read(p);h.update(status=s['status'],currentTile=s['currentTile'],currentPatch=s['currentPatch'],nextAction=s['nextStep'],inFlightStatus='none',fullyCovered4kCount=2,internalPassed4kCount=1,externalPassed4kCount=0,formalAcceptedCount=0,generatedNativeCount=len(records),gateAcknowledgment='capacity-gate-ack.json',riskInventory='capacity-road-building-risks.json',updatedAtUtc=now());h['pixelCoveredCandidates']=['tiles/r03_c12.png','tiles/r03_c13.png'];h['unfinishedSparseCandidate']='qa/r03_c14-existing-coverage-native.png';write(p,h)
p=ZONE/'tile-plan.json';t=read(p)
for q in t['tiles']:
 if q['id']=='r03_c12':q['status']='internal_passed_external_pending'
 if q['id']=='r03_c13':q['status']='fully_covered_internal_geometry_failed_gate_hold'
 if q['id']=='r03_c14':q['status']='partial13cores_gate_hold'
 if q['id']=='r04_c12':q['status']='prepared_no_native_gate_hold'
write(p,t)
print(json.dumps({'generatedNativeCount':len(records),'usableNativeCount':len(usable),'fullyCovered4kCount':2,'internalPassed4kCount':1,'formalAcceptedCount':0,'inFlightStatus':'none'}))

