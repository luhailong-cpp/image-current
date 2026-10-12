from native_work import *
import sys
name=sys.argv[1];failed=set(sys.argv[2:])
dp=ZONE/'tiles'/f'{name}.png.derivation.json';d=read(dp);qa=Path(d['inspectionCrops']);tid=d['tileId']
files=sorted(qa.glob('*.png'));assert len(files)==49
entries=[]
for p in files:
 with Image.open(p) as im:size=list(im.size)
 entries.append({'file':p.as_posix(),'sha256':sha(p),'size':size,'inspectionScale':1,'resized':False,'status':'requires_local_material_repair' if p.name in failed else 'passed_visual_100pct'})
review={'tileId':tid,'candidatePath':d['file'],'sha256':d['sha256'],'size':[4096,4096],'reviewer':'root','reviewedAtUtc':now(),'nativeCoreCount':16,'internalSeamCount':24,'internalCrossCount':9,'status':'requires_native_material_repair' if failed else 'complete_internal_QA_passed','internalReview':'requires_native_material_repair' if failed else 'passed16core24seam9cross_native1to1','inspectedCrops':entries,'pendingIssues':['Residual straight stone-face material boundary at native x1024 in r03_c10_p02_03_v2'] if failed else [],'externalSeams':'available core segments inspected; final tile boundary pending','formalAccepted':False,'finalArtUpscaled':False,'blending':'none'}
rp=ZONE/'qa'/f'{name}-review.json';write(rp,review)
d.update(internalReview=review['internalReview'],status=review['status'],reviewPath=rp.as_posix(),pendingIssues=review['pendingIssues']);write(dp,d)
s=read(ZONE/f'selection-{tid}.json');s.update(internalReview=d['internalReview'],pendingIssues=review['pendingIssues'],reviewPath=rp.as_posix(),updatedAtUtc=now());write(ZONE/f'selection-{tid}.json',s)
print(json.dumps({'reviewPath':rp.as_posix(),'status':review['status'],'inspectedCropCount':49,'failedCropCount':len(failed)}))
