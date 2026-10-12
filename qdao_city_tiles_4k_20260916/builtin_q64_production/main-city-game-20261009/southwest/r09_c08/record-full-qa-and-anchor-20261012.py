from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import sys,json,hashlib
B=Path(__file__).resolve().parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
def write(p,d):
 p=Path(p);assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def review():
 tile='r09_c08';t=B/tile;base=t/'pipeline/output/c60755460eef51ba/assembly.json';a=read(base)
 pending=[{'kind':'upper_inner_rim_terminates_at_invented_divider','corePoint':[3257,1240]}, {'kind':'lower_inner_rim_width_jump','corePoint':[3257,1669]}, {'kind':'inner_rim_small_notch','coreBox':[1940,2010,2140,2200]}, {'kind':'unfinished_horizontal_grout_stub','coreBox':[840,2020,1160,2290]}, {'kind':'outer_band_width_jump','corePoint':[115,135]}, {'kind':'imported_dense_cellular_material','scope':'grey stone bands; restrained finish repair pending'}, {'kind':'external_tile_seams_pending','neighborTiles':['r09_c07','r10_c08','r08_c08']}, {'kind':'global_ellipse_geometry_pending','scope':'large annular band and oversized meander panels'}]
 reviewed=['row04-native-20261012/whole-row.png','row04-native-20261012/vertical-x1024.png','row04-native-20261012/vertical-x2048.png','row04-native-20261012/vertical-x3072.png','horizontal_y3072_full.png','intersection_x1024_y3072.png','intersection_x2048_y3072.png','intersection_x3072_y3072.png']
 q=t/'pipeline/qa/c60755460eef51ba'
 write(q/'visual-review-20261012.json',{'tile':tile,'reviewedAtUtc':now(),'baseAssembly':str(base),'baseAssemblySha256':sha(base),'coreSha256':a['output']['sha256'],'contextSha256':a['contextOutput']['sha256'],'nativeSlots':16,'nativePreflightPassed':True,'fullCandidateVisuallyInspected':True,'allFourRowsNativeQaPerformed':True,'lastRowReviewedImages':[{'file':str(q/f),'sha256':sha(q/f)} for f in reviewed],'findings':'Last-row Taiji S border and ivory field continue correctly. Inner grey ring has two sharp elbows at core [905,3242] and [1114,3202]. Other previously recorded row1-3 geometry and material defects remain.','formalAccepted':False,'pending':pending})
 d=t/'repairs-resume-20261012/lower-rim-elbow-v01';g=read(d/'generation.json');ia=d/'integrated/assembly.json';ai=read(ia)
 Image.open(ai['output']['file']).crop((700,3000,1400,3450)).save(d/'integrated/native-review-crop.png')
 write(d/'visual-review-20261012.json',{'reviewedAtUtc':now(),'native':g['file'],'nativeSha256':g['sha256'],'receipt':str(d/'tool-result.json'),'receiptSha256':sha(d/'tool-result.json'),'visualDisposition':'Actual 1254x1254 returned PNG visually inspected: two short grey band border elbows smoothed; original crop framing and broad grey/ivory surfaces preserved. Full integrated4096 candidate visually inspected: original panel and Taiji layout preserved; other named defects remain. Native integration crop review follows.','formalAccepted':False,'integratedAssembly':str(ia),'integratedAssemblySha256':sha(ia),'pending':pending})
 progress=read(t/'production-resume-20261012.json');progress.update(selectedNativeCount=16,nextMissingCoordinate=None,status='full_candidate_provisional_pending_geometry_material_external_qa',selectedCandidateAssembly=str(ia),selectedCandidateSha256=ai['output']['sha256'],selectedContextSha256=ai['contextOutput']['sha256'],fullVisualQA=str(q/'visual-review-20261012.json'),pendingSeamReview=pending,updatedAtUtc=now(),nextTile='r10_c07',formalAccepted=False)
 (t/'production-resume-20261012.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'qa':str(q/'visual-review-20261012.json'),'nativeReviewCrop':str(d/'integrated/native-review-crop.png'),'selectedCandidate':ai['output']}))
def anchor(tile,assembly,side):
 assert tile in {f'r{r:02d}_c{c:02d}' for r in range(9,17) for c in (7,8)} and side in ('top','left')
 a=read(assembly);src=Path(a['contextOutput']['file']);assert sha(src)==a['contextOutput']['sha256']
 im=Image.open(src);assert im.size==(4326,4326)
 box=(0,4096,4326,4326) if side=='top' else (4096,0,4326,4326)
 p=B/tile/'pipeline/anchors'/f'{a["tile"]}-{side}-resume-20261012.png';assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);im.crop(box).save(p)
 write(str(p)+'.derivation.json',{'operation':'exact native context border crop','sourceAssembly':str(assembly),'sourceAssemblySha256':sha(assembly),'sourceContext':str(src),'sourceContextSha256':sha(src),'sourceCrop':list(box),'output':str(p),'outputSha256':sha(p),'pixels':list(Image.open(p).size),'sourceResampling':False,'formalAccepted':False,'upstreamStatus':'provisional candidate pending geometry/material/external QA','createdAtUtc':now()})
 print(json.dumps({'anchor':str(p),'sha256':sha(p)}))
if __name__=='__main__':
 {'review':review,'anchor':anchor}[sys.argv[1]](*sys.argv[2:])
