import sys,json,os
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
HERE=Path(__file__).resolve().parent;OUT=HERE/'checkpoint-v2';sources=p.read(OUT/'sources.json')
# Exact verification of newly applied small native derivations.
checks=[]
for name in ['flower-return01','roof-fragments01','roof-fragments02']:
 d=HERE/name;a=np.array(Image.open(d/('context-native.png' if name=='flower-return01' else 'current-base-context.png')).convert('RGB'));b=np.array(Image.open(d/'raw-v1.png').convert('RGB'));alpha=np.array(Image.open(d/'alpha.png').convert('L'));actual=np.array(Image.open(d/'derived-context.png').convert('RGB'));expect=((a.astype('uint32')*(255-alpha[...,None])+b.astype('uint32')*alpha[...,None]+127)//255).astype('uint8')
 assert np.array_equal(expect,actual);assert np.array_equal(actual[alpha==0],a[alpha==0]);checks.append({'derivation':name,'exactPixelReconstruction':True,'outsideSupportUnchanged':True})
for tile,src in sources.items():
 f=Path(src['file']);im=Image.open(f);assert im.size==(4096,4096) and p.sha(f)==src['sha256'];assembly=p.read(src['assembly']);assert assembly['candidate']['sha256']==p.sha(f)
 selected=[]
 for patch in p.patch_ids():
  nf=p.selected(ROOT/tile,patch);ni=p.native_info(nf);assert Image.open(nf).size==(1254,1254);selected.append({'patch':patch,'file':str(nf),'sha256':p.sha(nf)})
 checks.append({'tile':tile,'candidateSHA256':p.sha(f),'candidatePixels':[4096,4096],'validatedSelectedNativeOrDerivedPatches':len(selected),'selectedSources':selected})
for tile,subdir in [('r03_c05','south-v3'),('r04_c05','south-v3'),('r03_c05','flower-v1'),('r03_c05','fragments-v1')]:
 d=ROOT/tile/'continuation-20261011'/subdir;m=p.read(d/'integration-manifest.json');a=np.array(Image.open(m['baseCandidate']['file']).convert('RGB'));b=np.array(Image.open(m['integratedComposite']['file']).convert('RGB'));mask=np.array(Image.open(m['combinedSupport']['file']).convert('L'))>0;assert np.array_equal(a[~mask],b[~mask])
 checks.append({'integration':str(d),'outsideSupportUnchanged':True,'changedPixels':int(np.any(a!=b,2).sum())})
p.put_json(OUT/'verification.json',{'createdAt':p.now(),'allChecksPassed':True,'checks':checks,'southIndependentAudit':{'file':str(HERE/'merged-south-v3/independent-audit.json'),'sha256':p.sha(HERE/'merged-south-v3/independent-audit.json'),'role':'140 successful independent checks'},'formalAccepted':False})
# Reviews only claim views actually performed.
southViews=p.read(HERE/'merged-south-v3/root-visual-review.json')
r03Review={'createdAt':p.now(),'tile':'r03_c05','candidate':sources['r03_c05'],'baseReview':str(ROOT/'r03_c05/qa-review-native/final-visual-review.json'),'newChanges':{'E3_E4_E5_E6':'Four south structure conflicts repaired, all4 seam crops and returns viewed','D3':'Duplicate flower center repaired, confined radial alpha, native QA and changed internal crop viewed','D2':'Blue sawtooth/triangular/rectangular fragments cleaned in2 native contexts;9 changed internal/junction QA crops viewed'},'actuallyViewedChangedQA':[], 'remainingDefects':['D1 roof row/material phase discontinuity near y909,x0..2160','D4 repeated thin roof row/diagonal transition near y2960,x1900..4096; new2raw trials rejected due return ghosting','D5 gold beam joint straight facet; raw trial rejected due fresh bevel kinks','E1 west segment3 material tone step','E2 west segment4 misaligned eave troughs/flower edge'],'strictInternalFullyPassed':False,'formalAccepted':False,'fourway':{'file':str(OUT/'fourway-native.png'),'actuallyViewed':True,'verdict':'major geometry continuous; faint preexisting timber tone band remains at top of crop'},'rejectedTrials':[str(HERE/'gold-joint01/visual-review.json'),str(HERE/'roof-row-merge-v1/visual-review.json')]}
for stage in ['5174e832fa56','e28885c9de32','945fa7bcbb42']:
 f=ROOT/'r03_c05/candidate'/('r03_c05-pipeline-fixed-native-contexts-'+stage+'.assembly.json');m=p.read(f)
 for q in m['qaFiles']:
  if q['changedFromPreviouslyReviewedBase']:
   r03Review['actuallyViewedChangedQA'].append({'file':q['file'],'sha256':p.sha(q['file']),'actuallyViewed':True,'verdict':'new repaired ROI continuous; unrelated inherited defects remain','stage':stage})
p.put_json(OUT/'r03_c05-review.json',r03Review)
r04Review={'createdAt':p.now(),'tile':'r04_c05','candidate':sources['r04_c05'],'baseReview':str(ROOT/'r04_c05/final-delivery.json'),'newChanges':'Four north structure conflicts repaired and timber lower return corrected','actuallyViewedChangedQA':[],'independentNativeAudit':str(HERE/'merged-south-v3/independent-audit.json'),'remainingDefects':['Inherited internal mild wood tone differences,2..4px floor-line jog,grey-plinth tone band','Inherited south segment4 green blurry stripe at lion foot; strict quality remains FAIL'],'strictInternalFullyPassed':False,'formalAccepted':False}
for q in p.read(sources['r04_c05']['assembly'])['qaFiles']:
 if q['changedFromPreviouslyReviewedBase']:r04Review['actuallyViewedChangedQA'].append({'file':q['file'],'sha256':p.sha(q['file']),'actuallyViewed':True,'verdict':'major geometry continuous; mild material differences remain'})
p.put_json(OUT/'r04_c05-review.json',r04Review)
inventory=sorted(HERE.glob('neighbor-availability-*.json'))[-1]
remaining=['r03_c05: D1上层瓦行相位、D4重复窄瓦行、D5金梁接头仍待修；试修失败均未选入。','r03_c05/r03_c04西侧对接: 第3段材质色差、第4段瓦当/瓦沟错位仍在。','r03_c04: 左屋面两处回接待修，见既有final-candidate-review.json。','r04_c04: 栏板微小矩形色差仍在；r04_c05: 内部轻微材质/地面线残差及南侧第4段旧图狮脚绿色模糊带仍在。','6块外围邻图仍未提供所需24个原尺寸边界源，无法完成这些边界验收。','仅本分配四块候选；正式验收0/4，不代表整区或整图完成。']
tiles=[]
for tile,src in sources.items():
 review=OUT/(tile+'-review.json') if tile.endswith('05') else ROOT/tile/'final-candidate-review.json'
 supplementary=[str(OUT/'verification.json'),str(HERE/'merged-south-v3/root-visual-review.json'),str(HERE/'merged-south-v3/independent-audit.json'),str(inventory)] if tile.endswith('05') else [str(inventory)]
 tiles.append({'tile':tile,'candidate':src['file'],'assembly':src['assembly'],'review':str(review),'supplementaryReviews':supplementary})
p.put_json(HERE/'delivery-v2-spec.json',{'directory':'delivery-20261011-v2','tiles':tiles,'crossBoundarySummary':['右列上下4段结构冲突已修复，主要几何连续；局部材质差异仍如实记录。','左列上下接缝既有检查主要几何通过；下行左右接缝检查连续。','上行左右第3/4段既有问题仍待修。','四路交点原尺寸实看主要几何连续，裁图顶端有轻微木面色带。','最新外围邻图库存:'+str(inventory)],'remainingWork':remaining})
# Required continuation record, preserving the actual first new output.
state=p.read(ROOT/'continuation-round-20261011.json');previous={x['file'].replace('\\','/') for x in state['successfulSavedOutputsFromPreviousResume']}
allraw=[]
for f in HERE.glob('*/raw-*.png.generation.json'):
 rec=p.read(f);allraw.append({'file':rec['file'],'sha256':rec['sha256'],'pixels':[rec['width'],rec['height']],'hostSource':rec['hostSource'],'record':str(f),'submittedParameters':rec['submittedParameters'],'actualModel':None,'actualQuality':None})
new=[r for r in allraw if r['file'].replace('\\','/') not in previous]
state.update({'updatedAt':p.now(),'status':'verified_new_candidates_checkpoint_remaining_repairs','currentCoordinate':'r03_c05 internal roof D1/D4/D5; four assigned tiles only','candidateCount':4,'coveredAssignedCores':64,'internalFullyPassedTileCount':0,'formalAcceptedCount':0,'savedActualNewOutputsThisRound':new,'newRawOutputCountThisRound':len(new),'savedRawOutputCountAcrossRestoration':len(allraw),'integratedRawRepairSourceCountAcrossRestoration':8,'updatedCandidates':sources,'verification':str(OUT/'verification.json'),'newDeliveryManifest':str(ROOT/'delivery-20261011-v2/delivery-manifest.json'),'latestNeighborInventory':str(inventory),'nextStep':'Continue owned roof phase/row/gold-joint repairs from reviewed candidate945fa7bcbb42; do not select rejected trials. Wait for missing outer neighbors before boundary acceptance.','remainingWork':remaining,'gitOperationsThisRound':0,'errors':[],'resolvedLocalExecutionIssues':[{'issue':'First publish attempt found r03_c05/receipts directory absent','resolution':'Created only missing owned receipts directories, reran successfully; no source loss'}]})
tmp=HERE/'round-checkpoint-writing.json';p.put_json(tmp,state);os.replace(tmp,ROOT/'continuation-round-20261011.json')
local=p.read(ROOT/'local-continuation-20261011.json');local.update({'updatedAtUTC':p.now(),'status':state['status'],'newDeliveryManifest':state['newDeliveryManifest'],'currentCandidates':sources,'remainingWork':remaining,'nextStep':state['nextStep'],'unmergedAcceptedRepairCount':0,'rejectedOrPendingTrialFiles':[str(HERE/'south-segment04/raw-v1.png'),str(HERE/'gold-joint01/raw-v1.png'),str(HERE/'roof-row01/raw-v1.png'),str(HERE/'roof-row02/raw-v1.png')]})
tmp=HERE/'local-checkpoint-writing.json';p.put_json(tmp,local);os.replace(tmp,ROOT/'local-continuation-20261011.json')
print(json.dumps({'verified':True,'roundNewRawCount':len(new),'acrossRestorationRawCount':len(allraw),'integratedRepairSources':8,'deliverySpec':str(HERE/'delivery-v2-spec.json')}))

