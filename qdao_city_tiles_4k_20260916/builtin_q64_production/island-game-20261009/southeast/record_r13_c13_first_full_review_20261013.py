from workflow import *
q=ROOT/'qa/r13_c13-right-full-20261013-v01'
s=read(q/'seams.json')
failed={'h13':'Previous whole spar/join review remains not passed; retain for whole-object repair.','h21':'Independent water networks/material differ at actual p21/p22 boundary.','h23':'p23 upper-right rectangular guide artifact appears left of the real seam.','h41':'p41/p42 independent water networks break at actual vertical seam.','h43':'p43 upper-right rectangular guide artifact.','v11':'p11/p21 independently drawn water networks and density change along actual seam.','v13':'p23 upper-right water window rectangular artifact.','v33':'p43 upper-right water rectangle persists.'}
for e in s['entries']:
 e['status']='not_passed' if e['id'] in failed else 'passed'
 e['visualNote']=failed.get(e['id'],'Actual native-pixel seam viewed: connected geometry/material; no blocking defect on this seam.')
j=[]
for rr in range(1,4):
 for cc in range(1,4):
  rc=f'{rr}{cc}';f=q/f'junction_{rc}.png';j.append({'id':'junction_'+rc,'file':str(f),'sha256':sha(f),'status':'not_passed' if rc in ['11','13','21','31','33'] else 'passed','visualNote':'Actual 512 square native crop viewed; water mismatch/guide rectangle remains.' if rc in ['11','13','21','31','33'] else 'Actual native junction continuous.'})
out={'candidate':s['candidate'],'candidateSha256':s['candidateSha256'],'reviewedAtUtc':now(),'reviewer':'right_resume','internalSeams':s['entries'],'junctions':j,'seamCount':24,'junctionCount':9,'seamsPassed':16,'junctionsPassed':4,'internalAccepted':False,'externalAccepted':False,'formalAccepted':False,'sourceReplayMismatch':0,'coveredPixels':16777216,'knownWholeSourceIssues':['p11 native x230/y230 water material guide band after two repairs','p13 spar/body guide join deferred after two unsuccessful repairs','p41 native x230 water material band after two repairs'],'nextStep':'Complete independent r14_c13 first. Then use native candidate-only registered whole-object crops to repair listed defects; do not rerun old guides.'}
write(q/'actual-review.json',out)
pf=ROOT/'progress-r13_c13.json';d=read(pf);d.update({'complete4kCount':1,'internalPassed4kCount':0,'externalPassed4kCount':0,'formalAcceptedCount':0,'uniqueGeneratedPatchCoordinates':16,'fullCoverageCandidate':s['candidate'],'candidateSha256':s['candidateSha256'],'candidateStatus':'complete_16_native_core_coverage_NOT_PASSED','internalQA':str(q/'actual-review.json'),'updatedAt':now()});write(pf,d)
print({'candidate':s['candidate'],'internalPassed':False,'seamsPassed':16,'junctionsPassed':4})

