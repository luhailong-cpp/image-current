from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
from datetime import datetime,timezone
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest');D=R/'work-r03_c02/west-final';Q=D/'qa-final'
read=lambda p:json.loads(Path(p).read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=read(D/'final-joint.assembly.json');w=read(D/'r03_c02.west-final.assembly.json');e=read(D/'r03_c03.west-final.assembly.json')
mask=np.asarray(Image.open(e['deltaMask']['file']))>0;yy,xx=np.nonzero(mask);bbox=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)];globalbox=[bbox[0]+8192,bbox[1]+8192,bbox[2]+8192,bbox[3]+8192]
assert not np.any(mask[-115:]);assert globalbox[2]<11700
arr=np.asarray(Image.open(m['candidate']));e3=np.asarray(Image.open(R/'work-r03_c02/qa/e3-repair/e3-v09.native-contribution-rgb.png'));eid=np.asarray(Image.open(R/'work-r03_c02/qa/e3-repair/e3-v09.native-contribution-id.png'));e3mask=eid[:,:784]>0
assert int(e3mask.sum())==105775;assert np.array_equal(arr[589:2867,3312:4096][e3mask],e3[:,:784][e3mask])
raws=[]
for i in range(1001,1006):
 s=m['sources'][str(i)];g=read(s['generationRecord']);assert g['actualModel'] is None and g['actualQuality'] is None
 raws.append({'sourceId':i,'file':s['file'],'sha256':s['sha256'],'generationRecord':s['generationRecord'],'generationRecordSHA256':s['generationRecordSha256'],'actualModel':None,'actualQuality':None,'tool':'image_gen.imagegen','route':'builtin','nativeSize':[1254,1254]})
qa={'schemaVersion':1,'reviewedAt':datetime.now(timezone.utc).isoformat(),'status':'pass-for-requested-west-tile-interior-and-east-west-boundary','internalAccepted':True,'eastWestBoundaryAccepted':True,'formalAccepted':False,'scope':'r03_c02 interior and shared r03_c02/r03_c03 boundary. Whole-map formal acceptance and the three other external edges are outside this work item.','candidateWest':w['candidate'],'candidateEast':e['candidate'],'sourceIdWest':w['sourceIdMap'],'sourceIdEast':e['sourceIdMap'],'nativeProof':{'pixels':33554432,'sources':len(m['finalProof']['sources']),'mismatches':0,'resample':False,'blend':False,'feather':False,'colorRewrite':False},'newBuiltinSources':raws,'defects':[
 {'id':'M1','result':'pass','finding':'Beam-end face is continuous; original bright vertical strip removed.','qa':str(Q/'M1.png')},
 {'id':'G1','result':'pass','finding':'Diagonal rail meets its rounded cap continuously without the former upward notch.','qa':str(Q/'G1.png')},
 {'id':'M2','result':'pass','finding':'Shadowed window stays continuous below the former horizontal texture cutoff; right post has uninterrupted wood grain; foreground lantern and rail contours preserved.','qa':str(Q/'M2.png')},
 {'id':'E1','result':'pass','finding':'Existing roof bridge and actual native overlap preserve continuous eave, wooden header and bracket shadows.','qa':[str(Q/('roof-'+s+'.png')) for s in ['left','right','bottom']]},
 {'id':'E2','result':'pass','finding':'Rolled and folded cloth share coherent weave through the old boundary. Full silhouettes, curls, ties, paving and wooden tray edges continue across the actual hard masks. Bottom wood face finished using existing native source 513/520 on the west side only.','qa':[str(Q/'E2-bottom.png'),str(Q/'E2-right.png'),str(Q/'external-4.png')]},
 {'id':'E3','result':'pass-preserved','finding':'All 105775 required west-extension pixels are included exactly. Previously accepted east E3 and south pixels are unchanged.'}],
 'nativeScaleVisualReview':{'scale':1,'resampledForReview':False,'internalVerticalSegments':12,'internalHorizontalSegments':12,'internalJunctions':9,'sharedBoundaryLength':4096,'sharedBoundaryPanels':[str(Q/f'external-{i}.png') for i in range(1,5)],'internalPanels':[str(Q/f'internal-{o}-{i}.png') for o in ['v','h'] for i in range(1,5)],'junctionPanel':str(Q/'internal-nine-junctions.png'),'newMaskPerimetersAndDefects':'All five repair images were inspected whole at 1254 native resolution after integration; complete roof bridge left/right/bottom edges, cloth right/bottom cuts, and final west-only south corner were inspected again at 1:1.','result':'pass'},
 'preservation':{'E3WestRequiredPixels':105775,'E3WestMismatches':0,'eastProtectedPixels':e['E3AndSouthProtectedPixels'],'eastProtectedChangedPixels':0,'eastBottom115Mismatches':0,'rootCenterFootRepairGlobalBox':[11700,11700,12954,12954],'deltaOverlapWithRootCenterFootRepair':0},'eastDelta':{'baseline':e['baseline'],'mask':e['deltaMask'],'sourceIdMap':e['deltaSourceIdMap'],'pixels':e['deltaPixels'],'tileBoundsExclusive':bbox,'globalBoundsExclusive':globalbox,'mergeRule':'At each nonzero delta-mask pixel only, copy RGB from r03_c03.west-final.png and source ID from r03_c03.west-final.delta-source-id.png; retain all other current root pixels. Source IDs refer to the attached assembly source registry.'}}
qp=D/'west-final.visual-review.json';qp.write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8')
arts=[]
for tile,record in [('r03_c02',w),('r03_c03',e)]:
 record.update(status='passed-requested-interior-and-shared-boundary-review',eastWestBoundaryAccepted=True,visualReview={'file':str(qp),'sha256':sha(qp)})
 if tile=='r03_c02':record['internalAccepted']=True
 else:
  record.pop('internalAccepted',None)
  record.update(westDeltaAccepted=True,internalReviewScope='Baseline retained outside scoped west delta; full east interior not re-audited in this west repair.',deltaBoundsTileExclusive=bbox,deltaBoundsGlobalExclusive=globalbox)
 p=D/(tile+'.west-final.assembly.json');p.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8');arts.append({'file':str(p),'sha256':sha(p),'candidate':record['candidate']})
m.update(tileArtifacts=arts,visualQA='passed-requested-interior-and-shared-boundary',visualReview={'file':str(qp),'sha256':sha(qp)})
(D/'final-joint.assembly.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'artifacts':arts,'qa':{'file':str(qp),'sha256':sha(qp)},'jointAssemblySHA256':sha(D/'final-joint.assembly.json'),'eastDelta':qa['eastDelta'],'westSouthFinishSelectedPixels':m['southLeftObjectFinish']['selectedPixels']},ensure_ascii=False))
