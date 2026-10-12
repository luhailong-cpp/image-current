from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
records=[]
for i in range(9,16):
 D=B/f'fix{i:02}_centered'; raw=D/'generated-centered.png';params=json.loads((D/'parameters.json').read_text(encoding='utf-8'));e=json.loads((D/'generation-evidence.json').read_text(encoding='utf-8'))
 e['submittedReferences']=[{'file':p,'sha256':sha(p),'pixels':list(Image.open(p).size)} for p in params['referenced_image_paths']]
 e['submittedReference']=params['referenced_image_paths'][0];e['submittedReferenceSha256']=sha(e['submittedReference']);e['formalAccepted']=False
 (D/'generation-evidence.json').write_text(json.dumps(e,indent=2),encoding='utf-8')
 for suffix in ['.png.derivation.json','.png.generation.json']:
  p=D/f's04_01_fix{i:02}_centered_derived{suffix}';r=json.loads(p.read_text(encoding='utf-8'));r['visualQA']='rejected: raw centered repair does not preserve the fixed south rail cross-section; source-selected reintegration still has visible bevel/groove discontinuity';r['formalAccepted']=False;p.write_text(json.dumps(r,indent=2),encoding='utf-8')
 records.append({'version':f'fix{i:02}_centered','raw':str(raw),'rawSha256':sha(raw),'pixels':list(Image.open(raw).size),'worldBox':[12173,15757,13427,17011],'generationEvidence':str(D/'generation-evidence.json'),'derived':str(D/f's04_01_fix{i:02}_centered_derived.png'),'formalAccepted':False,'actualModel':None,'actualQuality':None})
out={'scope':'r04_c04/s04_01 south boundary only','status':'stopped_further_generation_on_parent_instruction; no centered repair accepted','builtInToolCalls':7,'actualModel':None,'actualQuality':None,
 'sharedSelectionOrProgressModified':False,'oldSouthSourceModified':False,'derivativePixels':'Same-world-coordinate source selection only; binary minimum-error seams; no resize, blend, feather, color correction or code-painted artwork',
 'originalCandidateRetained':str(B/'fix08/generated.png'),'originalCandidateAccepted':False,
 'failureLocation':{'northNativeXApprox':[650,785],'northNativeYApprox':[1024,1139],'worldXApprox':[12823,12958],'worldYApprox':[16269,16384],'secondaryRightGrooveNativeXApprox':[906,926]},
 'finding':'The generator modifies several rail cross-section edges and shading independently in the reference south half. A continuous raw centered image does not prove continuity with the unmodified actual south source. Reintroducing the actual south reveals different lateral offsets at the gray side face, cream bevel and inset grooves.',
 'viewedRawOutputs':[f'fix{i:02}_centered/generated-centered.png' for i in range(9,16)],
 'viewedDerivedUpperAndSouthFullAndDetail':['fix09_centered','fix10_centered','fix11_centered','fix13_centered','fix15_centered'],
 'fix12And14':'Raw images visually rejected; derived files retained for traceability but no claim of complete derived visual inspection.',
 'earlierFix01Audit':{'file':str(B.parent/'native/s04_01_fix01.png'),'overlapLeftMAE':2.944904347826087,'overlapRightMAE':2.5342995169082125,'fullNativeViewed':True,'finding':'Low overlap error reflects preserved bottom anchor only. Full native has a conspicuous internal geometric break at y1024. Not a valid ready-to-use replacement.'},
 'toolAvailability':'Tool calls succeeded. This is continuity instability, not claimed API failure, quota exhaustion or tool blockage.','records':records}
(B/'centered-repair-handoff.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'handoff':str(B/'centered-repair-handoff.json'),'centeredCount':len(records),'all1254':all(r['pixels']==[1254,1254] for r in records)},indent=2))
