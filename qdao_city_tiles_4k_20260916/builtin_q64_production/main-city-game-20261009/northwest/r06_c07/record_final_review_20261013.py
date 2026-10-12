"""Bind explicitly viewed native QA crops to this immutable hard candidate."""
from pathlib import Path
import sys,json,importlib.util
T=Path(__file__).resolve().parent;Z=T.parent
spec=importlib.util.spec_from_file_location('p',Z/'production_v2.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
name='r06_c07-candidate-hard-4c0d654c3aae';m=p.read(T/'candidate'/(name+'.assembly.json'));out=m['output'];assert p.sha(out['file'])==out['sha256']
external=p.read(T/'qa'/(name+'.actual-final-neighbors')/'manifest.json');assert len(external['crops'])==15
def review(ref,note,status='passed'):
 assert p.sha(ref['file'])==ref['sha256']
 return dict(file=ref['file'],sha256=ref['sha256'],actuallyViewed=True,viewDetail='original',nativePixelScale=1,status=status,notes=note)
internal=[]
for ref in m['qa']:
 n=Path(ref['file']).stem
 status='pending_independent_rib_review' if n=='internal-y3072-segment02' else 'passed'
 note='Connected grout, wood contours, roof glaze rows, lantern paper ribs and caps as applicable; no free end or rectangular cutoff.'
 if status!='passed':note='Possible slight lantern-rib kink at native seam near x650/x760; independent root check requested before final internal verdict.'
 internal.append(review(ref,note,status))
p.write_json(T/'qa'/(name+'.internal-review-pending-rib.json'),dict(candidate=out,reviewer='/root/resume_r06_c07_finish',actuallyViewed=True,viewDetail='original',seamSegments=24,junctions=9,viewedCount=33,passedCount=32,pendingCount=1,formalAccepted=False,crops=internal))
ext=[]
for ref in external['crops']:
 ext.append(review(ref,'Viewed actual final4096 neighbor boundary at original native scale. Main slab/grout and highlights, road rim, roof glaze/contour and gold ornament connect as applicable; fine stone-grain variations are natural. No rectangular hard cutoff.'))
p.write_json(T/'qa'/(name+'.actual-neighbor-review.json'),dict(candidate=out,reviewer='/root/resume_r06_c07_finish',actuallyViewed=True,viewDetail='original',status='passed_available_north_west',requiredCrops=14,extraNorthwestCorner=1,viewedCount=15,reviewedSides=['north','west'],actualNorth=external['actualNorth'],actualWest=external['actualWest'],actualNorthwest=external['actualNorthwest'],formalAccepted=False,pendingSides=['east','south'],crops=ext))
print(json.dumps(dict(internalViewed=33,internalPassed=32,internalPending=1,externalViewed=15,externalPassed=15,formalAccepted=False)))
