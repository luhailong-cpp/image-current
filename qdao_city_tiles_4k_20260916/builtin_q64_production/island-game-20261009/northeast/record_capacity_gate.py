"""Gate acknowledgment and existing-output inventory; no generation or global writes."""
from native_work import *
gate=ZONE.parents[1]/'capacity-layout-gate-20261010.json'
# gate is one level above island-game map directory
if not gate.exists(): gate=ZONE.parent.parent/'capacity-layout-gate-20261010.json'
out=[]
for p in sorted((ZONE/'native').glob('*.png')):
 recp=p.with_suffix('.png.generation.json');r=read(recp) if recp.exists() else {}
 with Image.open(p) as im: size=list(im.size)
 out.append({'id':p.stem,'file':p.as_posix(),'sha256':sha(p),'nativeSize':size,'coordinateBoxArtPixels':r.get('coreWorldBox'),'recordExists':recp.exists(),'status':r.get('status','missing_record'),'isRepair':'_cross_' in p.stem})
coords={}
for r in out:
 if r['coordinateBoxArtPixels'] is not None and not r['isRepair']: coords.setdefault('_'.join(r['id'].split('_')[:4]),r['coordinateBoxArtPixels'])
ack={'schemaVersion':1,'zone':'northeast','receivedAtUtc':now(),'gateFile':gate.as_posix(),'gateSha256':sha(gate),'gateStatus':read(gate)['status'],'acknowledged':True,'newImageRequestsHeld':True,'rootInFlightStatus':'none; last r03_c13_p04_03_v2 finished and ingested before gate received','workerInFlightStatus':{'native_column':'notified; awaiting current invocation save acknowledgment','provenance_audit':'notified; awaiting current invocation save acknowledgment'},'inFlightStatus':'root none; child confirmations pending','generatedNativeCount':len(out),'generatedCoordinates':coords,'nativeInventory':out,'worldSize':None,'capacity5000Validated':False,'preserveExistingArtwork':True,'allowedWork':'existing-only mechanical assembly, native100pct QA, provenance replay and road/building risk inventory','releaseAuthority':'delegating root after layout/scale review'}
write(ZONE/'capacity-gate-ack.json',ack)
p=read(ZONE/'progress.json');p.update(status='capacity_layout_gate_existing_only_QA',generatedNativeCount=len(out),fullyCovered4kCount=len(list((ZONE/'tiles').glob('*.png'))),internalPassed4kCount=1,externalPassed4kCount=0,capacity5000Validated=False,updatedAtUtc=now(),nextStep='No new image requests; assemble/replay existing pixels and inventory geometry risks pending capacity gate release.');write(ZONE/'progress.json',p)
print(json.dumps({'nativeCount':len(out),'coreCoordinates':len(coords),'ack':(ZONE/'capacity-gate-ack.json').as_posix()}))

