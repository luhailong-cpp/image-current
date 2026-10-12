from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import production as p
prefix='east-r09c05-groundselect-v02-r09_c05'
rp=ROOT/'qa'/f'{prefix}-report.json';report=p.load(rp)
notes={'tile':'r09_c05','reviewedAtUtc':p.now(),'status':'complete 4K native candidate reviewed with west boundary exceptions','reviewedNativeStrips':24,'reviewedNativeJunctions':9,'rawReviewManifest':str(ROOT/'qa'/'c04-hardseam-east-r09c05-v01-native-QA-manifest.json'),'changes':[{'repair':'r09_c05_cap_round_v01','result':'single squared cap corrected to round ivory ball; complete target and four native perimeters reviewed; passed'},{'operation':'source selection only','oldSourceId':9,'newSourceId':10,'pixelCount':2676,'result':'removed blurred gray paving fragment; native target and surrounding seams reviewed; passed'}],'rejectedTrials':[{'prefix':'east-r09c05-groundselect-v01','reason':'overlarge ROI introduced bottom paving line shift; not selected'}],'acceptedNotes':['Small natural painterly texture differences in bamboo foliage and stone faces; no displaced major culm or wall contour in interior.','Existing foreground cap has soft painterly detail; no internal geometry gap.'],'remainingBoundaryIssues':[{'region':'west strip tile-local x0..115','nearLocalY':[909,1950,3185],'issue':'preserved c04 border strip has material/leaf/frame discontinuity against new native artwork; needs c04/c05 shared edge review and local source repair','scope':'outside edge pending'}],'allOuterTileEdgesPassed':False,'formalAccepted':False,'stablePrefix':prefix,'sameGlobalCoordinateExact':True,'validatedPixels':16777216,'mismatchedPixels':0}
qa=ROOT/'qa'/'east-r09c05-native-review.json';p.dump(qa,notes)
d=p.load(ROOT/'qa'/'expansion-east-worker-map.json');art=report['outputs'][0];mask=report['outputs'][1]
d.setdefault('candidateArtifacts',{})['r09_c05']={**art,'sourceIdMask':mask['path'],'sourceReport':str(rp),'record':str(rp),'review':str(qa),'status':notes['status'],'nativeSourceCount':len(report['inputs']),'allOuterTileEdgesPassed':False,'formalAccepted':False}
d['qa']['r09_c05_cap_round_v01']={'status':'selected_local_repair','note':'Round ball target and all four native perimeters visually passed.','formalAccepted':False}
d['status']='continuing_next_tile';d['completeCandidateTiles']=['r09_c05'];p.dump(ROOT/'qa'/'expansion-east-worker-map.json',d)
print(json.dumps({'candidate':art,'review':str(qa),'nativeSourceCount':len(report['inputs'])}))
