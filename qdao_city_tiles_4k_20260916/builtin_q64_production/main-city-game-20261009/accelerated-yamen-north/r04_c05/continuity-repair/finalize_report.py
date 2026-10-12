from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).parent.parent; D=T/'continuity-repair/merged-v2'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=T/'candidate/r04_c05-pipeline-minimum-error-e2769dba9467-6e5fcf.assembly.json';a=json.loads(ap.read_text())
residual={
'internal-y1024-segment01.png':'Minor localized dark timber tonal patch at the join; upright geometry remains continuous.',
'internal-y2048-segment03.png':'Small approximately 2-4 native pixel height/shape jog in one pavement mortar line near tile x2048,y2020; no large structural displacement.',
'junction-x2048-y2048.png':'Same small pavement mortar-line jog as internal-y2048-segment03.',
'internal-x2048-segment03.png':'Residual muted tonal transition on gray plinth face below landing, with aligned major edge.',
'internal-x2048-segment04.png':'Faint vertical material band remains on gray plinth face; no broken geometry.',
'junction-x2048-y3072.png':'Same faint gray plinth-face material-band residual.'}
for q in a['qaFiles']:
 name=Path(q['file']).name;q['actuallyViewed']=True;q['visualVerdict']='minor_residual' if name in residual else 'pass_major_continuity';q['observation']=residual.get(name,'No obvious broken contour or disconnected architectural/object feature in this native-scale crop.')
a['internalQA']={'status':'reviewed_with_minor_residuals','actuallyViewed':True,'nativeCropsViewed':33,'majorContinuityPassCrops':27,'minorResidualCrops':6,'formalAccepted':False}
a['sourceDerivation']={'manifest':str(D/'derivation.json'),'singleToolNativeOutput':False,'nativeResolutionMultiSource':True,'resampled':False,'narrowAlphaBandWidth':128,'actualModel':None}
ep=T/'qa/final-external/manifest.json';e=json.loads(ep.read_text())
for q in e['externalCrops']:
 name=Path(q['file']).name;q['actuallyViewed']=True
 if name=='south-segment04.png':
  q['verdict']='residual_quality_issue';q['observation']='Inherited blurred green horizontal area under the lion feet remains visibly soft and not a resolved carved material; its shape follows existing southern reference. Not a strict quality pass.'
 else:q['verdict']='pass_major_continuity';q['observation']='Door, landing/stair or stone rail/plinth lines remain continuous across the displayed true boundary; no major contour offset observed.'
e['status']='reviewed_with_south_segment04_quality_residual';e['nativeCropsViewed']=8;ep.write_text(json.dumps(e,ensure_ascii=False,indent=2))
a['externalQA']={'status':'partial_review_with_known_residuals','actuallyViewed':True,'thisWorkerNativeCropsViewed':8,'manifest':str(ep),'west':'4/4 major continuity pass against actual r04_c04 final candidate','south':'3/4 major continuity pass; segment04 inherited blur residual','north':'4/4 structural conflicts reported by north owner; updated-final-candidate supplement handled by root/boundary owner; not passed here','east':'waiting for neighbor material, 0/4 available; not passed'}
ap.write_text(json.dumps(a,ensure_ascii=False,indent=2))
# Extract exact prompt texts; existing parameters.json remains the exact built-in request.
for p in list((T/'tool-work').glob('*/parameters.json'))+list((T/'continuity-repair').glob('*/parameters.json')):
 try:
  obj=json.loads(p.read_text(encoding='utf-8'));prompt=obj.get('prompt')
  if prompt and not (p.parent/'prompt.txt').exists():(p.parent/'prompt.txt').write_text(prompt,encoding='utf-8')
 except Exception:pass
m=json.loads((D/'derivation.json').read_text());m['repairJoinAdditional']={'sourceId':18,'purpose':'actual imagegen staircase seam-center geometry repair','nativeWorldBox':[16781,15130,18035,16384],'weights':'source-18-weights-u16.png','recipe':str(T/'continuity-repair/merge_native_v2.py'),'noResampling':True}
m['visualQA']={'status':a['internalQA']['status'],'report':str(T/'final-delivery.json'),'formalAccepted':False}
(D/'derivation.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
native=[]
for p in sorted((T/'native').glob('*.png')):
 r=Path(str(p)+'.generation.json');im=Image.open(p);native.append({'file':str(p),'pixels':list(im.size),'sha256':sha(p),'generationRecord':str(r),'actualModel':None})
report={'tile':'r04_c05','status':'candidate_delivered_with_documented_residuals','formalAccepted':False,'candidate':a['candidate'],'assemblyManifest':str(ap),'finalSelection':str(T/'pipeline-selection.json'),'nativeOriginals':native,'selectedNativeCoreCount':16,'builtinOnly':True,'paidApiUsed':False,'actualModel':None,'rawToolEvidenceDirectories':[str(T/'tool-work'),str(T/'continuity-repair/shaft-cord-v1'),str(T/'continuity-repair/shaft-cord-v2'),str(T/'continuity-repair/stairs-v1')],'derivationManifest':str(D/'derivation.json'),'verification':str(D/'verification.json'),'selectedSourceCount':18,'narrowAlphaBandWidthPixels':128,'weightDenominator':65535,'resampled':False,'blended':True,'nativeToolOutput':False,'description':'4096 candidate assembled from sixteen1254x1254 built-in native source patches plus two selected1254x1254 built-in seam repair sources; all are sampled at the same world coordinate. This is explicitly a weighted derived assembly, not a single native tool image.','internalQA':a['internalQA'],'internalQAFiles':a['qaFiles'],'externalQA':a['externalQA'],'externalQAFiles':e['externalCrops'],'remainingInternalIssues':residual,'remainingExternalIssues':['North boundary structural conflicts remain according to north-owner QA; new final candidate supplement is handled by root.','South segment04 contains an inherited unresolved blurred green area beneath lion feet.','East neighbor r04_c06 missing:0/4 native patches available, cannot evaluate.'],'outer160PixelBandComparisonToFirstCandidate':json.loads((D/'outer-band-comparison.json').read_text()),'outerBandComparisonBaseline':str(T/'candidate/r04_c05-pipeline-minimum-error-94abcdd4569b-241dfc.png'),'nextAction':'Parent consolidation/review; no more generation or edits performed after final candidate freeze.'}
(T/'final-delivery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'report':str(T/'final-delivery.json'),'candidate':a['candidate'],'internalViewed':33,'externalViewed':8,'formalAccepted':False},ensure_ascii=False,indent=2))

