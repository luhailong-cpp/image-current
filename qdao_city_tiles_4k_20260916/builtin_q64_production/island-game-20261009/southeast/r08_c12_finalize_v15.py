from pathlib import Path
from PIL import Image
import json,hashlib,copy
from datetime import datetime,timezone
import numpy as np
R=Path(__file__).resolve().parent
assert __import__('os').environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def eq(a,b):return a.size==b.size and a.tobytes()==b.tobytes()
now=datetime.now(timezone.utc).isoformat()
qa=R/'qa';cand=R/'tiles/r08_c12.candidate-v15.png';im=Image.open(cand).convert('RGB')
old=rd(qa/'r08_c12.resume-review-final.json')
if 'v13.png' in old['candidate'] and not (qa/'r08_c12.resume-review-v13.json').exists():wr(qa/'r08_c12.resume-review-v13.json',old)
replay=rd(qa/'r08_c12.replay-v15.json');audit=rd(qa/'r08_c12.source-audit-v15.json')
assert replay['replayPixelExact'] and replay['allSourceHashesMatch'] and replay['allNative1254']
auditok=all(all(r[k] for k in ['shaMatch','promptExists','promptNonempty','promptShaMatch','receiptExists','actualModelNull','actualQualityNull','configSnapshotIsTargetOnly','sourceHostHashMatch']) and r['nativeSize']==[1254,1254] and all(x['exists'] and x['shaMatch'] for x in r['references']) for r in audit['records'])
assert auditok and audit['count']==42
# Flatten the historical overlay sequence to once-only, currently visible source ownership.
def subtract(a,b):
 x0,y0,x1,y1=a;u0,v0,u1,v1=b;ix0,iy0,ix1,iy1=max(x0,u0),max(y0,v0),min(x1,u1),min(y1,v1)
 if ix0>=ix1 or iy0>=iy1:return [a]
 return [q for q in [[x0,y0,x1,iy0],[x0,iy1,x1,y1],[x0,iy0,ix0,iy1],[ix1,iy0,x1,iy1]] if q[0]<q[2] and q[1]<q[3]]
def clipped(p,box):
 q=copy.deepcopy(p);x,y=p['destinationBox'][:2];sx,sy=p['sourceCrop'][:2]
 q['sourceCrop']=[sx+box[0]-x,sy+box[1]-y,sx+box[2]-x,sy+box[3]-y];q['destinationBox']=box;q['destination']=box[:2];return q
parts=[]
for p in replay['sources']:
 parts=[clipped(q,b) for q in parts for b in subtract(q['destinationBox'],p['destinationBox'])]
 parts.append(copy.deepcopy(p))
coverage=np.zeros((4096,4096),dtype=np.uint8);render=Image.new('RGB',(4096,4096));sources={}
for p in parts:
 f=Path(p['file']);assert sh(f)==p['sha256']
 a=Image.open(f).convert('RGB').crop(p['sourceCrop']);x0,y0,x1,y1=p['destinationBox'];assert a.size==(x1-x0,y1-y0)
 render.paste(a,(x0,y0));coverage[y0:y1,x0:x1]+=1;sources[str(f)]=p['sha256']
assert np.all(coverage==1) and eq(im,render)
ownership={'createdAt':now,'candidate':str(cand),'sha256':sh(cand),'operation':'Once-only visible source rectangles flattened from the chronological 16 base cores and 14 overlays; exact native crop and paste only.','visibleNativeCount':len(sources),'visibleRectangleCount':len(parts),'pixelCoverageMin':int(coverage.min()),'pixelCoverageMax':int(coverage.max()),'replayPixelExact':True,'resize':False,'blend':False,'warp':False,'contributions':parts,'actualModel':None,'actualQuality':None,'formalAccepted':False}
wr(qa/'r08_c12.final-visible-source-map-v15.json',ownership)
# Inspectable changed/unchanged evidence: unchanged crops inherit their previous actual visual review.
grid=[];junction=[]
for axis in 'hv':
 for j in range(1,4):
  for s in range(1,5):
   name=f'{axis}{j}-s{s}';p=qa/f'r08_c12.v13-{name}.png';q=qa/f'r08_c12.v15-{name}.png'
   same=eq(Image.open(p).convert('RGB'),Image.open(q).convert('RGB'))
   grid.append({'id':name,'file':str(q),'sha256':sh(q),'pixelIdenticalToV13':same,'reviewBasis':'Inherited previously viewed pixels after exact comparison' if same else 'Direct native visual review of v15','status':'internal_geometry_pass'})
for j in range(1,4):
 for s in range(1,4):
  name=f'{j}{s}';p=qa/f'r08_c12.junction_{name}-v13.png';q=qa/f'r08_c12.junction_{name}-v15.png'
  same=eq(Image.open(p).convert('RGB'),Image.open(q).convert('RGB'))
  junction.append({'id':name,'file':str(q),'sha256':sh(q),'pixelIdenticalToV13':same,'reviewBasis':'Inherited previously viewed pixels after exact comparison' if same else 'Direct native visual review of v15','status':'internal_geometry_pass'})
assert sum(not x['pixelIdenticalToV13'] for x in grid)==7 and sum(not x['pixelIdenticalToV13'] for x in junction)==2
north=[];idx=rd(qa/'roof-surface-v01/review-index.json');south=Image.open(R/'tiles/r09_c12.candidate-v04.png').convert('RGB')
for c in range(3):
 f=qa/f'roof-surface-v01/north-{c+1}.png';q=Image.open(f).convert('RGB')
 box=[1024*c,3840,1024*(c+1),4096];n=eq(q.crop((0,0,1024,256)),im.crop(box));s=eq(q.crop((0,256,1024,512)),south.crop((1024*c,0,1024*(c+1),256)))
 assert n and s
 north.append({'id':f'north-{c+1}','file':str(f),'sha256':sh(f),'r08Source':str(cand),'r08SourceCrop':box,'topHalfPixelExactToV15':n,'r09Source':str(R/'tiles/r09_c12.candidate-v04.png'),'r09SourceCrop':[1024*c,0,1024*(c+1),256],'bottomHalfPixelExactToV04':s,'trueTileBoundaryLocalY':256,'visualStatus':'geometry_continuous','finding':'Rounded blue tile end contacts track the curved tile lip and occur at varying y coordinates; there is no common y256 clipping or tonal step.' if c==1 else 'Blue roof channels or gold ridge and adjacent foliage remain continuous at y256.','formalAccepted':False})
wr(qa/'r08_c12.v15-final-review-evidence.json',{'createdAt':now,'candidate':str(cand),'sha256':sh(cand),'gridSeams':grid,'junctions':junction,'northEdgeChecks':north,'northScopeNote':'These three files contain r09 v04 pixels; final newer r09 version and remaining edges belong to root acceptance.','sourceAuditAll42Pass':auditok,'formalAccepted':False})
# The old two-tile proposal is historical; update r08-side visible contribution after coping redraw.
proposal=rd(qa/'r08_c12-r09c12-final-split-proposal.json')
if not (qa/'r08_c12-r09c12-split-proposal-v13.json').exists():wr(qa/'r08_c12-r09c12-split-proposal-v13.json',proposal)
proposal['updatedAt']=now;proposal['r08Candidate']=str(cand);proposal['r08Sha256']=sh(cand)
proposal['historicalInitialSplitContributions']=copy.deepcopy(proposal['preciseNonOverlappingContributions'])
visible=[]
for p in proposal['preciseNonOverlappingContributions']:
 q=copy.deepcopy(p)
 if Path(q['native']).name=='r08_c12_repair_roof_shared_v01.png':
  q['r08SourceCrop']=[115,184,1139,696];q['r08DestinationBox']=[1536,3584,2560,4096]
 q['r08VisiblePixelsExact']=eq(Image.open(q['native']).convert('RGB').crop(q['r08SourceCrop']),im.crop(q['r08DestinationBox']))
 assert q['r08VisiblePixelsExact']
 visible.append(q)
proposal['preciseNonOverlappingContributions']=visible
p=R/'native/r08_c12_repair_coping_long_left_v01.png';sc=[115,1070,1139,1139];db=[1536,3515,2560,3584]
assert eq(Image.open(p).convert('RGB').crop(sc),im.crop(db))
proposal['r08OnlyReplacementWithinHistoricalRoofStrip']={'native':str(p),'sha256':sh(p),'sourceCrop':sc,'destinationBox':db,'pixelExact':True,'reason':'69 upper rows of the old shared-roof strip are now owned by the complete coping redraw; actual bottom512 rows and cross-tile roof boundary remain unchanged.'}
proposal['nonOverlappingSplitPixelExact']=True
proposal['currentVisibleR08SourceMap']='qa/r08_c12.final-visible-source-map-v15.json'
proposal['rootAction']='Historical r09 proposal was already applied by root to r09 v03, followed by root-owned roof refinements. Do not reapply it over newer r09 candidates. Verify the final root-selected r09 candidate against current r08 v15.'
proposal['parentReportedR09Application']={'appliedAtVersion':'v03','laterReportedVersion':'v06','ownership':'root','finalVersionNotYetIndependentlyReviewed':True}
proposal['northEdgeEvidence']='qa/r08_c12.v15-final-review-evidence.json'
wr(qa/'r08_c12-r09c12-final-split-proposal.json',proposal)
# Final review and scoped progress; formal acceptance remains with root.
final=copy.deepcopy(old)
final.update({'reviewedAt':now,'candidate':str(cand),'sha256':sh(cand),'internalGeometry':'All24 grid seams and all9 junctions are continuous. j32 is now a single planar coping run with a coherent existing right-post attachment.','internalCandidateAccepted':True,'formalAcceptedCount':0,'externalUsableAccepted':False,'sharedRoofProposalReadyForRoot':True,'openIssues':[],'evidenceManifest':'qa/r08_c12.v15-final-review-evidence.json','replay':'qa/r08_c12.replay-v15.json','sourceAudit':'qa/r08_c12.source-audit-v15.json','visibleSourceOwnership':'qa/r08_c12.final-visible-source-map-v15.json','newResumeNativeCount':16,'totalSavedR08NativeCount':42,'selectedBaseCores':16,'selectedRepairOverlays':14,'visibleNativeCount':len(sources),'inFlight':False})
final['resolved'].append('j32 artificial coping height step and extra foreground ledge; two coordinated complete native windows now form one wall cap')
final['materialNotes']=['Mild painted brush-density/value variation persists in stone/paving, without a visible disconnected contour or hard rectangular geometry jump in reviewed evidence.']
final['pendingRootReview']=['Final latest r09 candidate shared edge after its root-owned material repairs; only r09 v04 north-1/2/3 was independently viewed here.','External north/east/west neighbors and formal overall acceptance are outside this internal candidate decision.']
final['roofFindings']=['north-1/2/3 upper256 rows exactly match current r08 v15 bottom256 rows. Their lower256 rows exactly match r09 v04.','No y256 hard cut is seen in these three strips; north-2 curved tile lips must not be mistaken for a straight coordinate-boundary step.','r08 coping replacement overwrites69 upper rows of the third historical roof strip; the current ownership manifest records this accurately. Actual bottom512 rows are unchanged.','Original counterpart-v11 remains a historical exact proposal; root already applied and refined the r09 side.']
final['unselectedResumeImages']=['r08_c12_repair_roof_v02','r08_c12_repair_coping_v03','r08_c12_repair_coping_v04','r08_c12_repair_coping_long_left_v02']
final['newCopingPerimeterEvidence']=['qa/r08_c12.v14-overlay-left.png','qa/r08_c12.v14-overlay-top.png','qa/r08_c12.v14-overlay-bottom.png','qa/r08_c12.v15-overlay-left.png','qa/r08_c12.v15-overlay-right.png','qa/r08_c12.v15-overlay-top.png','qa/r08_c12.v15-overlay-bottom.png']
final['historicalReview']='qa/r08_c12.resume-review-v13.json'
wr(qa/'r08_c12.resume-review-final.json',final)
progress=rd(R/'progress-r08_c12.json');progress.update({'status':'internal_candidate_ready_for_root_review','updatedAt':now,'generatedNativeCount':42,'candidate4kCount':1,'currentCandidate':str(cand),'currentCandidateSha256':sh(cand),'selectedRepairOverlayCount':14,'selectedVisibleNativeCount':len(sources),'inFlight':False,'internalCandidateAccepted':True,'formalAcceptedCount':0,'externalUsableAccepted':False,'nextStep':'Root review v15 and final root-selected r09 shared boundary; do not reapply historical proposal over newer r09.','lastError':None})
wr(R/'progress-r08_c12.json',progress)
print(json.dumps({'candidate':str(cand),'sha256':sh(cand),'visibleSources':len(sources),'visibleRectangles':len(parts),'source42AuditPass':auditok,'replayPixelExact':True,'changedGridReviewed':7,'inheritedGrid':17,'changedJunctionsReviewed':2,'inheritedJunctions':7,'north3TopInheritance':True,'internalCandidateAccepted':True,'formalAccepted':False},indent=2))

