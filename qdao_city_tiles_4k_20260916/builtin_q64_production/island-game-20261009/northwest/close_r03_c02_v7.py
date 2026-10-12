from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent;q=Z/'qa/r03_c02_v7_internal_closure'
fi=lambda p:{'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
rd=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
p=Z/'tiles/r03_c02_candidate-v7_4096.png';record=p.with_suffix('.native-repair.json')
v=rd(q/'native_replay_validation.json');assert v['status']=='base_native_coverage_reverified' and v['base']['sha256']==fi(p)['sha256']
a=np.array(Image.open(p).convert('RGB'));b=np.array(Image.open(Z/'tiles/r03_c02_candidate-v1_4096.png').convert('RGB'))
edge={k:int(np.any(x!=y,axis=1).sum()) for k,x,y in [('north',a[0],b[0]),('south',a[-1],b[-1]),('west',a[:,0],b[:,0]),('east',a[:,-1],b[:,-1])]}
chain=[]
for n in range(2,8):
 rp=Z/'tiles'/f'r03_c02_candidate-v{n}_4096.native-repair.json';d=rd(rp);chain.append({'record':fi(rp),'output':d['output'],'cropBox':d['cropBox'],'mask':d['mask'],'selectedPixels':d['selection']['repairPixelCount']})
rec={'schemaVersion':1,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'west_closure','tileId':'r03_c02','candidate':fi(p),'candidateRecord':fi(record),'sourceManifest':fi(Z/'r03_c02.candidate-v1.manifest.json'),'nativeSourceCount':16,'selectedAttemptMatrix':[['a01','a02','a03','a02'],['a01','a01','a01','a02'],['a02','a01','a01','a02'],['a01','a01','a01','a02']],'standardCropCount':33,'nativeScale100Percent':True,'v5All33VisuallyReviewed':True,'v7DeltaReview':rd(q/'delta_from_v5.json'),'allChangedCropsVisuallyReviewed':True,'all33CropsCoveredByCurrentOrPixelIdenticalPriorReview':True,'internalClosurePassed':True,'closedFindings':['Gold guard join and blue blade facet discontinuities repaired.','Full lower-left paving run repaired, followed by three repair-boundary short cuts.','Two remaining blind paving grooves near tile (940,2050) and (950,2265) now connect into existing slab boundaries.'],'independentReview':[{'reviewer':'root','passed':['guard repair','blade repair a03 mask v2','paving_boundary union mask v2','paving_mid_tip mask v1 including upper tip']},{'reviewer':'right_completion','passed':['guard 1254 native composite','blade 1254 native composite'],'finding':'Nearby second paving blind tip found and subsequently repaired in v7.'}],'repairChain':chain,'nativeReplayValidation':fi(q/'native_replay_validation.json'),'fullNativeCoverage':True,'verifiedPixelCount':v['proof']['verifiedPixelCount'],'externalEdgePixelDeltasFromV1':edge,'externalEdgesValidated':False,'formalAccepted':False,'formalAcceptedCount':0,'qaIndex':fi(q/'qa_index.json'),'method':{'builtinImageGeneration':True,'resizingFinalArt':False,'registration':False,'feathering':False,'colorCorrection':False,'onlySameCoordinateNativePixels':True},'nextReview':'Connected tile edges; continue r04_c02 using unchanged south edge.'}
(q/'review.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'candidate':fi(p),'record':fi(record),'review':fi(q/'review.json'),'edges':edge}))
