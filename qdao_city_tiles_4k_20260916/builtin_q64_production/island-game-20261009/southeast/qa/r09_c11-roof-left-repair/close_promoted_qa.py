from pathlib import Path
from PIL import Image
import hashlib,json
from datetime import datetime,timezone
Q=Path(__file__).resolve().parent;R=Q.parent.parent
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def wr(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def same(a,b):return Image.open(a).convert('RGB').tobytes()==Image.open(b).convert('RGB').tobytes()
now=datetime.now(timezone.utc).isoformat();m=rd(Q/'promoted-manifest.json');external=Q/'promoted-external';ext=[]
for i in [1,2]:
 p=external/f'shared-{i}.png';prior=Q/f'whole-object-shared-{i}-v05.png';assert same(p,prior)
 ext.append({'file':str(p),'sha256':sh(p),'status':'geometry_pass','reviewMethod':'Pixel identical to directly reviewed whole-object v05 native-scale evidence','prior':str(prior)})
for i in [3,4]:
 p=external/f'shared-{i}.png';ext.append({'file':str(p),'sha256':sh(p),'status':'geometry_pass','reviewMethod':'Direct native-scale view after promotion','finding':'Wood panel borders, red/gold decoration and lower beam/stone joins are continuous on the actual x256 seam; inherited faint material texture varies without broken contour.'})
for i in range(1,5):
 p=external/f'north-{i}.png';prior=Q/'whole-object-r08north-1-v05.png' if i==1 else R/'qa/roof-final-north-independent'/f'north-{i}.png';assert same(p,prior)
 ext.append({'file':str(p),'sha256':sh(p),'status':'geometry_pass','reviewMethod':'Pixel-identical replay of directly reviewed native-scale boundary strip','prior':str(prior)})
for o in m['outputs']:
 folder=Path(o['QA']);delta=rd(folder/'prior-reviewed-pixel-replay.json');seams=rd(folder/'seams.json')
 for e in seams['entries']:e['status']='pixel_identical_inherit_prior_review' if e['unchanged'] else 'native_scale_visual_pass'
 wr(folder/'seams.json',seams)
 for e in delta['entries']:e['status']='pixel_identical_inherit_prior_review' if e['unchanged'] else 'native_scale_visual_pass'
 delta['status']='all_24_seams_9_junctions_reviewed_or_exactly_inherited';delta['reviewedAt']=now;wr(folder/'prior-reviewed-pixel-replay.json',delta)
 review={'tile':o['tile'],'candidate':o['candidate'],'sha256':o['sha256'],'reviewedAt':now,'reviewer':'coordinate_audit; root explicitly approved whole-object trial before promotion','status':'internal_pass_with_minor_material_notes','changedSeamsAndJunctionsDirectlyViewed':o['changedEntries'],'unchangedEvidenceCount':33-len(o['changedEntries']),'priorPixelReplay':str(folder/'prior-reviewed-pixel-replay.json'),'changedFinding':'Actual full-size promoted crops preserve whole gold terminal discs, roof mouths, black gutters and wood beams. No strong vertical material bar, severed tile or separated double contour.','minorNotes':['Two small 5-8px upper-to-whole dark-gutter corners near r09c11 [3635,495] and [3778,511], with localized triangular blue tone variation. Root explicitly accepted these as minor and requested no further generation.','Small shadow-width change near r09c11 [3310,1085]; complete single gutter and collar remain connected.','Earlier accepted material notes outside this changed region are inherited; see prior root review.'],'independentObjectReview':str(Q/'whole-object-v05-review.json'),'sourceAudit':o['sourceAudit'],'sourceRGBMismatchPixels':0,'flattenedNativeSourceCount':o['sourceCount'],'externalBoundaryEvidence':ext,'c11NorthFutureNeighbor':'r08c11 not yet generated; its true edge must be anchored to this promoted version.','formalAccepted':False,'usableExternalAccepted':False,'rootProgressAndProductionStateUpdated':False}
 wr(folder/'root-review.json',review)
 for p in [Path(o['candidate']+'.generation.json'),Path(o['sourceAudit'])]:
  a=rd(p);a['status']='internal_pass_with_minor_material_notes';a['finalReview']=str(folder/'root-review.json');wr(p,a)
 o['sourceAuditSha256']=sh(o['sourceAudit']);o['rootReview']=str(folder/'root-review.json');o['rootReviewSha256']=sh(folder/'root-review.json')
m['status']='promoted_internal_pass_with_minor_material_notes';m['reviewedAt']=now;m['externalEvidence']=ext;m['rootProgressAndProductionStateUpdated']=False;wr(Q/'promoted-manifest.json',m)
print(json.dumps({'status':m['status'],'manifest':str(Q/'promoted-manifest.json'),'sha256':sh(Q/'promoted-manifest.json'),'outputs':m['outputs']},indent=2))
