from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parent;S=R.parent/'crossedge-stair-restored-20261011'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
a=np.array(Image.open(S/'stair-combined/input.png')).astype(float)
b=np.array(Image.open(R/'premixed.png')).astype(float)
def centroid(z):
 w=np.maximum(0,-np.diff(z,axis=0))
 return float(np.sum(w*np.arange(len(z)-1))/max(1e-6,w.sum()))
metrics=[]
for x in range(440,900,25):
 before=40497+centroid(a[1177:1203,x:x+25].mean(axis=(1,2)))
 after=40497+centroid(b[30:56,x-320:x-295].mean(axis=(1,2)))
 metrics.append({'worldX':[x+19853,x+19878],'originalBevelCentroidY':before,'supplementBevelCentroidY':after,'deltaPixels':after-before})
qa={'status':'first_bevel_reuse_looks_improved_second_unresolved','atUtc':datetime.now(timezone.utc).isoformat(),'reviewedNativeCrops':['40507-original.png','40507-upper.png','40507-native.png','40507-translated.png','40734-original.png','40734-native.png','40734-translated.png','input.png','premixed.png'],'firstBevel':{'worldY':40507,'conclusion':'Use existing upper native at its original 1:1 world coordinates. Thin patch removes the obvious short vertical tonal jump without the uniform 3-pixel translation.','comparison':'Viewed native before/after 660x80 crops; the bevel runs continuously and the outer thin patch does not introduce an obvious rectangular color band.','bevelMeasurement':'Raw maximum-gradient peak varies among several small neighboring peaks, so a 3-4px shift inferred from a single averaged peak is not a reliable geometric correction. Gradient centroid across the full bevel is the supporting check.','centroidProbes':metrics,'maximumAbsoluteCentroidChangePixels':max(abs(z['deltaPixels'])for z in metrics)},'secondBevel':{'worldY':40734,'conclusion':'No reliable local translation proposal. The only native covering this y retains a local left/right height kink; uniform translation preserves that kink and moves other correctly aligned regions.','whyNoUniform4PixelMove':'Eight x-band edge probes differ: translated edge locations span world y40733..40739, including 3-7px unwanted movement relative to corresponding source segments.','remainingWorldRegion':[20353,40726,20553,40743],'status':'unresolved_no_artifact_for_merge'},'changedExistingDeliveredProposal':False,'changedTileOrContext':False,'sourceResampling':False,'networkCalls':0,'imageGenerationCalls':0,'formalAccepted':False}
write(R/'qa.json',qa)
p=json.loads((R/'proposal.json').read_text());p['qa']=str(R/'qa.json');p['qaSha256']=sha(R/'qa.json')
write(R/'proposal.json',p)
m={'status':'one_local_reuse_proposal_delivered_second_defect_recorded','networkCalls':0,'imageGenerationCalls':0,'onlyMergeProposal':{'file':str(R/'proposal.json'),'sha256':sha(R/'proposal.json'),'worldBox':p['worldBox'],'affectedWorldBox':p['affectedWorldBox']},'qa':{'file':str(R/'qa.json'),'sha256':sha(R/'qa.json')},'secondBevelUnresolved':True,'previousStairCombinedProposalUnchanged':sha(S/'stair-combined/proposal.json')==p['dependsOnProposalSha256'],'previousStairCombinedPremixedUnchanged':sha(S/'stair-combined/premixed.png')==p['expectedParentPremixedSha256'],'mergeOrder':['Apply existing stair-combined first','Validate supplemental input under mask','Copy this supplemental premixed once through copy-mask'],'actualModel':None,'actualQuality':None,'completedAtUtc':datetime.now(timezone.utc).isoformat()}
write(R/'manifest.json',m)
print(json.dumps({'manifest':str(R/'manifest.json'),'sha256':sha(R/'manifest.json'),'maxBevelCentroidChange':qa['firstBevel']['maximumAbsoluteCentroidChangePixels'],'proposalSha256':sha(R/'proposal.json'),'previousUnchanged':m['previousStairCombinedProposalUnchanged']and m['previousStairCombinedPremixedUnchanged']}))
