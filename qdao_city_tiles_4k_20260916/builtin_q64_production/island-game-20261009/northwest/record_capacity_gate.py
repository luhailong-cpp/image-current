from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re
Z=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
gate=Z.parents[1]/'capacity-layout-gate-20261010.json'
assert gate.exists()
coords={};others=[];records=[]
for p in sorted((Z/'native').glob('*.png')):
 gen=Path(str(p)+'.generation.json')
 rec=json.loads(gen.read_text(encoding='utf-8-sig')) if gen.exists() else {}
 item=dict(path=p.relative_to(Z).as_posix(),sha256=sha(p),generationRecord=gen.relative_to(Z).as_posix() if gen.exists() else None,nativeSize=[rec.get('nativeWidth'),rec.get('nativeHeight')])
 m=re.fullmatch(r'(r\d\d_c\d\d_s\d\d_\d\d)_(a\d+)\.png',p.name)
 if m:coords.setdefault(m.group(1),[]).append(item)
 else:others.append(item)
prepared=[]
for p in sorted((Z/'guides').glob('r??_c??_s??_??_a*.input.json')):
 stem=p.name.removesuffix('.input.json')
 if not (Z/'native'/f'{stem}.png').exists():prepared.append(dict(stem=stem,input=p.relative_to(Z).as_posix(),hasReceipt=(Z/'receipts'/f'{stem}.receipt.json').exists()))
style=Path('D:/work/image/designs/mail-ui-v1/01-mail-event.png')
ack=dict(schemaVersion=1,zone='northwest',recordedAtUtc=datetime.now(timezone.utc).isoformat(),gate=dict(path=gate.as_posix(),sha256=sha(gate),status=json.loads(gate.read_text(encoding='utf-8-sig'))['status']),acknowledged=True,allWorkersInstructed=True,inFlightStatus=dict(root='none',audit_contract='none',bottom_qa='none',continue_native='none; last r04_c03_s02_04_a02 attempt failed reference-read with no image output'),newImageGenerationAllowed=False,newCoordinatesAllowed=False,releaseAuthority='parent master after capacity/layout validation; this zone cannot release',target4kCount=49,scopeCancelled=False,preserveExistingArtwork=True,coordinateCount=len(coords),generatedNativeCount=sum(len(v) for v in coords.values())+len(others),generatedCoordinates=coords,otherNativeRepairsAndDiagnosticSources=others,preparedWithoutNative=prepared,fullyCovered4kCount=1,internalPassed4kCount=0,externalPassed4kCount=0,formalAcceptedCount=0,current4kCandidate='tiles/r03_c03_candidate-v5_4096.png',worldSize=None,capacity5000Validated=False,clientMappingValidated=False,additionalObservedBlock=dict(referencePath=style.as_posix(),exists=style.exists(),expectedSha256='3cf0b7d7b3bae337d51e947719588419a01ae21bdce9bccedd6258ce1feef0a2',note='Required primary style file missing at its recorded path. Do not infer it is deleted permanently or silently replace historical reference. No attempt to regenerate while gate active.'))
(Z/'capacity-gate-ack.json').write_text(json.dumps(ack,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pp=Z/'progress.json';p=json.loads(pp.read_text(encoding='utf-8-sig'))
p.update(status='capacity_layout_gate_active_readonly_QA',generationHold=True,gate=gate.as_posix(),generatedNativeCount=ack['generatedNativeCount'],fullyCovered4kCount=1,internalPassed4kCount=0,externalPassed4kCount=0,formalAcceptedCount=0,complete4kCount=0,latest4kCandidate=ack['current4kCandidate'],nextStep='Finish existing-pixel internal verification and inventory/risk review; wait for parent release before any further image generation or new coordinates.',updatedAtUtc=ack['recordedAtUtc'])
pp.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(coordinates=len(coords),nativeCount=ack['generatedNativeCount'],styleReferenceExists=style.exists(),ack=(Z/'capacity-gate-ack.json').as_posix())))
