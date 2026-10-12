from native_work import *
contract=read(ZONE.parent/'production-contract.json');resume=read(ZONE.parent.parent/'resume-production-20261010/production-resume.json')
refs=read(ZONE/'reference-audit.json')['references'][:2]
style=Path(contract['primaryStyleReference']);assert sha(style)==contract['primaryStyleSha256']
refs.append({'file':style.as_posix(),'sha256':sha(style),'size':list(Image.open(style).size),'role':'primary approved user-provided Daoist Q painting; same approved direction as missing oldPNG, distinct source; no UI/night','authority':'updated production-contract and production-resume20261010'})
for r in refs: assert Path(r['file']).exists() and sha(r['file'])==r['sha256']
write(ZONE/'reference-audit-resumed-20261010.json',{'checkedAtUtc':now(),'references':refs,'supersedesForFutureCallsOnly':'reference-audit.json','historyUnchanged':True,'batchPolicy':'Current restored config target2.5/max; builtin actual model/quality remain null','configSnapshot':read(ROOT/'config/image-generation.json')})
ack={'zone':'northeast','resumedAtUtc':now(),'status':'production_resumed','authority':(ZONE.parent.parent/'resume-production-20261010/production-resume.json').as_posix(),'newArtworkGenerationAllowed':True,'builtinOnly':True,'currentCoordinates':['r03_c13 terrace repair','r03_c14 missingp04_02..04 and2cross repairs','r04_c12 p01_01'],'nextMilestone':['r03_c12','r03_c13','r04_c12','r04_c13'],'targetTiles':49,'generatedNativeCountAtResume':len(list((ZONE/'native').glob('*.png'))),'fullyCovered4kCount':2,'internalPassed4kCount':1,'formalAcceptedCount':0,'styleReference':refs[-1],'worldSize':None,'capacity5000Validated':False,'nextStep':'Native whole terrace joint repair; parallel south neighbor production; finish existing east fragment without extending beyond it until2x2 closes.'}
write(ZONE/'resume-ack-20261010.json',ack)
p=read(ZONE/'progress.json');p.update(status='resumed_native_production',updatedAtUtc=now(),nextStep=ack['nextStep'],activeTiles=['r03_c13','r03_c14','r04_c12'],inFlightStatus='preparing new authorized requests')
for e in p['errors']:
 if e.get('stage') in ['shared input availability','approved style reference availability']:e.update(resolved=True,recovery='Restored config and explicitly approved userJPG replacement for future calls; historical evidence unchanged.',resolvedAtUtc=now())
write(ZONE/'progress.json',p)
h=read(ZONE/'handoff.json');h.update(status=p['status'],nextAction=p['nextStep'],resumeAcknowledgment='resume-ack-20261010.json',updatedAtUtc=now());write(ZONE/'handoff.json',h)
print(json.dumps({'resumed':True,'newStyle':refs[-1]}))

