from pathlib import Path
import json,datetime,hashlib,re
B=Path(__file__).resolve().parent;T=B/'r13_c13'
gate=B.parent.parent/'capacity-layout-gate-20261010.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
pr=read(B/'progress.json');g=read(gate);active=read(T/'active-native-map.json');coords=read(T/'coordinates.json')
records=[]
for logical,version in sorted(active.items()):
    p=T/'native'/f'{version}.png';rec=read(str(p)+'.generation.json')
    assert p.is_file() and sha(p)==rec['sha256']
    records.append({'logicalPatch':logical,'activeVersion':version,'coreBox':rec['coordinates']['coreBox'],'contextBox':rec['coordinates']['contextBox'],'nativeFile':str(p),'nativeSize':[rec['width'],rec['height']],'sha256':rec['sha256']})
repairs=[]
for p in sorted((T/'repairs').glob('*-native.png.generation.json')):
    rec=read(p);native=Path(rec['file']);assert native.exists() and sha(native)==rec['sha256']
    repairs.append({'id':rec['id'],'tileBox':rec['targetMetadata']['cropBoxIn4096'],'nativeFile':str(native),'nativeSize':[rec['width'],rec['height']],'sha256':rec['sha256']})
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
ack={'schemaVersion':1,'receivedAtUtc':now,'zone':'southeast','gateFile':str(gate),'gateSha256':sha(gate),'gateStatus':g['status'],'acknowledged':True,'generationHoldActive':True,'newImageGenCallsAfterGate':0,'inFlightStatus':{'imageGen':'none','pendingNativeResults':0,'startedNewImageCallsThisResumption':0,'note':'No image generation was active or started before gate arrived in this resumption.'},'internalWorkers':[{'name':'/root/seam_audit','statusAtGate':'completed_idle','newAssignment':'read-only existing-art capacity-sensitive road/building risk inventory','generationProhibited':True}],'generatedTileCoordinates':[{'tile':'r13_c13','coreBox':[49152,49152,53248,53248],'candidateFile':pr['candidateFile'],'candidateSha256':pr['candidateSha256'],'fullyCovered':True,'internalQaPassed':True,'externalPassed':False,'formalAccepted':False,'activeCorePatches':records,'nativeRepairContributions':repairs}],'historicalGeneratedNativeCount':29,'activeCorePatchCount':16,'nativeRepairCount':7,'fullyCovered4kCount':1,'internalPassed4kCount':1,'externalPassed4kCount':0,'formalAcceptedCount':0,'plannedTileCount':64,'missingFullyCoveredTileCount':63,'missingFormalTileCount':64,'worldSize':None,'capacity5000Validated':False,'preserveExistingArtwork':True,'willNotReleaseGateIndependently':True,'nextAllowedWork':'Provenance replay, existing-art visual QA and road/building risk inventory only; await root release before new artwork.'}
(B/'capacity-gate-ack.json').write_text(json.dumps(ack,ensure_ascii=False,indent=2),encoding='utf-8')
pr.update(updatedAt=now,status='capacity_layout_gate_active_existing_art_review',capacityGateActive=True,capacityGateFile=str(gate),capacityGateAck=str(B/'capacity-gate-ack.json'),inFlightImageGenCount=0,fullyCovered4kCount=1,internalPassed4kCount=1,externalPassed4kCount=0,missingFullyCoveredTileCount=63,missingFormalTileCount=64,usableNativeCorePatchCount=16,nextStep=ack['nextAllowedWork'])
(B/'progress.json').write_text(json.dumps(pr,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'ack':str(B/'capacity-gate-ack.json'),'inFlight':'none','generatedTiles':['r13_c13'],'corePatchCount':16,'repairNativeCount':7,'missingFullyCoveredTiles':63,'formalAccepted':0}))

