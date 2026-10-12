from workflow import *
tid='r13_c12';p=read(ROOT/f'progress-{tid}.json');p['workingVersions'].update({'33':'v01','43':'v01'});assert len(p['workingVersions'])==16
write(ROOT/f'{tid}-native-spec-20261013-v01.json',{'tile':tid,'patchVersions':p['workingVersions'],'overlayManifests':[str(ROOT/'proposed-overlay-r13_c12-stair-20261012-v02.json')],'operation':'Exact native cores plus a complete staircase object native crop, unchanged pixels only'})
p.update(updatedAt=now(),status='complete_native_cores_candidate_assembly',missingPatches=[],inFlight=False,inFlightRequests=[]);write(ROOT/f'progress-{tid}.json',p)
p=read(ROOT/'progress-r14_c12.json');p['workingVersions'].update({'11':'v01','12':'v01','14':'v01'});p.update(updatedAt=now(),inFlight=False,inFlightRequests=[]);write(ROOT/'progress-r14_c12.json',p)
print('16 root13 coordinates plus complete staircase source recorded;14 first row3 sources saved.')
