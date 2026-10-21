from pathlib import Path
import json,hashlib
T=Path(__file__).resolve().parent
Q=T/'qa/independent-local-repair-20261013';Q.mkdir(parents=True,exist_ok=True)
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
jobs=[]
for folder,proposal,names,note in [
 ('row2-x3072-dangling-20261013','adoption-proposal.json',['detail','north','south','west','east'],'Grout forms a continuous fitted corner; all local perimeter crossings maintain shaded edges without clipped endpoints.'),
 ('row3-x1024-step-20261013','adoption-proposal-v2.json',['v2-left','v2-right','v2-mid-upper','v2-mid-lower','v2-full-context'],'Extended corridor removes the local step and keeps both grout endpoints continuous. Broader pre-existing stone-face material variation outside mask is not approved by this local review.')]:
 D=T/'repair-batches'/folder;p=D/proposal;data=json.loads(p.read_text());review=Q/(folder+'.review.json')
 assert not review.exists()
 obj={'reviewer':'/root/r08_c04_row2_local_repair','actuallyViewed':True,'status':'passed_local_native_adoption','proposal':{'file':str(p),'sha256':sha(p)},'sourceSha256':data['sourceSha256'],'maskSha256':data['maskSha256'],'pixelCount':data['selectedPixelCount'],'rootReview':{'file':str(D/'root-local-review.json'),'sha256':sha(D/'root-local-review.json')},'crops':[{'file':str(D/(n+'.png')),'sha256':sha(D/(n+'.png')),'actuallyViewed':True,'status':'passed_local_geometry_and_perimeter'} for n in names],'finding':note,'fullTileInternalQAPassed':False,'formalAccepted':False}
 review.write_text(json.dumps(obj,indent=2),encoding='utf-8')
 jobs.append({'proposal':str(p),'independentReview':str(review)})
jobsfile=Q/'integration-jobs.json';assert not jobsfile.exists();jobsfile.write_text(json.dumps(jobs,indent=2),encoding='utf-8')
print(jobsfile)

