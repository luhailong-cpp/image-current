from pathlib import Path
import json,os,uuid
Z=Path(__file__).resolve().parent;T=Z/'r12_c10';p=T/'selected-patches.json'
s=json.loads(p.read_text(encoding='utf-8-sig'))
g=Z/'seam-qa/G3-shared-stairs-resume-20261012/root-G3-joint-adoption-20261012.json'
if 'wallJointAdoption' in s:
 assert Path(s['wallJointAdoption']).resolve()==g.resolve()
 s['G3JointAdoption']=str(g);del s['wallJointAdoption']
 s['geometryBlockingIssues']=[v for v in s.get('geometryBlockingIssues',[]) if v!='G3']
 s.update(G3GeometryReview=str(g.parent/'root-v3-independent-geometry-review.json'),G3MaterialStatus='material_finish_pending',materialPending=True,internalReady=False,formalAccepted=False)
 tmp=p.with_name(p.name+'.metadata-'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(tmp,p)
print(json.dumps(dict(tile=s['tile'],G3JointAdoption=s.get('G3JointAdoption'),internalReady=s['internalReady'])))
