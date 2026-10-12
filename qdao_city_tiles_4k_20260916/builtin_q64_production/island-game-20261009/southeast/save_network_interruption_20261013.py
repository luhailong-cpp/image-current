from workflow import *
tid='r14_c12';d=read(ROOT/f'progress-{tid}.json');versions={}
for r in range(1,5):
 for c in range(1,5):
  rc=f'{r}{c}';f=ROOT/'native'/f'{tid}_p{rc}_v01.png'
  if f.exists():
   im=Image.open(f);assert im.size==(1254,1254)
   meta=read(Path(str(f)+'.generation.json'));assert meta['sha256']==sha(f)
   assert Path(meta['sourceOutputPath']).exists() and sha(Path(meta['sourceOutputPath']))==sha(f)
   versions[rc]='v01'
missing=[f'{r}{c}' for r in range(1,5) for c in range(1,5) if f'{r}{c}' not in versions]
d.update(updatedAt=now(),workingVersions=versions,selectedNativeCoreCount=len(versions),generatedNativeCount=len(versions),status='interrupted_application_network_permission_revoked',inFlight=False,inFlightRequests=[],lastError='image generation failed: application network permission was revoked',missingNativeCoordinates=missing,fullyCovered4kCount=0,internalPassed4kCount=0,externalPassed4kCount=0,formalAcceptedCount=0,nextStep='Restore normal application network permission, then resume p33 v01 from saved exact request; prepare p43 only after p33 succeeds. Do not regenerate 14 saved original patches.')
write(ROOT/f'progress-{tid}.json',d)
write(ROOT/'receipts/r14_c12_p33_v01.error.json',{'tool':'image_gen.imagegen','route':'builtin','request':str(ROOT/'prompts/r14_c12_p33_v01.args.json'),'requestSha256':sha(ROOT/'prompts/r14_c12_p33_v01.args.json'),'status':'failed_no_image_returned','error':'image generation failed: application network permission was revoked','recordedAtUtc':now(),'retryPerformed':False,'permissionBypassPerformed':False})
resume=read(ROOT/'production-resume-20261012.json')
counts=resume['counts'];counts['generatedNativeCount']=len(list((ROOT/'native').glob('*.png')))
interruption={'recordedAtUtc':now(),'error':'application network permission was revoked','rootFailedRequest':'r14_c12_p33_v01','rootSavedNativeCount':len(versions),'rootMissingNativeCoordinates':missing,'rootSuccessfulUnsavedOutputs':0,'allRootReturnedOriginalsPreservedWithExactSourceHash':True,'agentsInterrupted':['left_resume_sol','right_resume_sol','wall_resume_sol'],'furtherNetworkRetriesPerformed':False,'permissionBypassPerformed':False,'nativeReview':'14 saved sea natives visually viewed; full actual 4K seam/junction review awaits missing p33 and p43; not counted full or internally accepted','nextAction':'Resume current native request only after application network permission is restored; finish map before deferred skill installation or model investigation.'}
write(ROOT/'network-interruption-20261013.json',interruption)
resume.update(updatedAtUtc=now(),counts=counts,status='interrupted_application_network_permission_revoked',generationStopped=True,inFlightRequests=[],currentTile=tid,networkInterruption=interruption,nextStep=interruption['nextAction'])
write(ROOT/'production-resume-20261012.json',resume)
for fname in ['progress.json','production-state.json']:
 p=read(ROOT/fname);p.update(updatedAt=now(),status='interrupted_application_network_permission_revoked',currentTile=tid,generationStopped=True,inFlight=False,inFlightRequests=[],lastError=interruption['error'],nextStep=interruption['nextAction'],networkInterruption=interruption)
 if fname=='progress.json':p.update(**counts)
 else:p['counts']=counts
 write(ROOT/fname,p)
p=read(ROOT/'current-zone-counts-20261013.json');p.update(updatedAtUtc=now(),counts=counts,status='interrupted_application_network_permission_revoked',networkInterruption=interruption);write(ROOT/'current-zone-counts-20261013.json',p)
print(json.dumps({'counts':counts,'r14_c12':{'selected':len(versions),'missing':missing},'rootSuccessfulUnsavedOutputs':0}))
