"""Record actual visual review scope; no generation or image modification."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
SW=Path(__file__).resolve().parents[2]
TAG='local-review-20261013-v01'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
viewed={
 'r09_c01':['main-intersections.png','main-vertical-x1024.png','main-vertical-x2048.png','main-vertical-x3072.png','main-horizontal-y1024.png','main-horizontal-y2048.png','main-horizontal-y3072.png'],
 'r09_c02':['main-intersections.png','main-vertical-x2048.png','main-horizontal-y3072.png','external-r09_c01-to-r09_c02.png'],
 'r09_c03':['main-intersections.png','main-vertical-x2048.png','main-vertical-x3072.png','left4x2-horizontal-y3072.png','bottom-left-two-available-cores.png','external-r09_c02-to-r09_c03.png']
}
findings={
 'r09_c01':[
  {'id':'c01-blue-board-tone','kind':'material_seam','priority':1,'approximateTilePixelBox':[250,905,1200,1143],'patches':['p01_01','p01_02','p02_01','p02_02'],'evidence':['main-horizontal-y1024.png','main-intersections.png'],'observation':'Same curved turquoise roof-board surface has a hard irregular horizontal shade/brush-density boundary near y1024, crossing multiple boards without a physical joint.','futureRepairIntent':'Unify painted blue-board tone and grain over the existing shape; preserve gold silhouette and board grooves.'},
  {'id':'c01-brown-plane-tone','kind':'material_seam','priority':2,'approximateTilePixelBox':[1929,1792,2167,2816],'patches':['p02_02','p02_03','p03_02','p03_03'],'evidence':['main-vertical-x2048.png','main-intersections.png'],'observation':'Broad sloped brown surface retains a narrow vertical tone/brush transition around x2048; continuity is unresolved.','futureRepairIntent':'Match one continuous surface material without moving its outline, tree shadows or adjacent roof.'},
  {'id':'c01-background-tone','kind':'material_seam','priority':1,'approximateTilePixelBox':[1929,2816,2167,4096],'patches':['p03_02','p03_03','p04_02','p04_03'],'evidence':['main-vertical-x2048.png','main-intersections.png','main-horizontal-y3072.png'],'observation':'Unjointed grey-brown background below the sloped plane has a conspicuous jagged vertical light/dark boundary near x2048, continuing behind the lower lantern.','futureRepairIntent':'Repaint only the background material/shadow continuity at native scale; preserve lantern and timber edges.'}
 ],
 'r09_c02':[
  {'id':'c02-medallion-rim-notch','kind':'geometry_seam','priority':1,'approximateTilePixelBox':[1980,3072,2250,3335],'patches':['p04_02','p04_03'],'evidence':['main-intersections.png','main-vertical-x2048.png'],'observation':'Lower gold medallion rim terminates in an angular tooth/notch and a sudden finish change around the center join. The circular outer profile does not continue.','futureRepairIntent':'Restore a single circular lower rim at fixed medallion position/scale with continuous native gold finish.'},
  {'id':'c02-wall-pattern-tone','kind':'material_seam','priority':1,'approximateTilePixelBox':[1929,3328,2167,4096],'patches':['p04_02','p04_03'],'evidence':['main-vertical-x2048.png'],'observation':'Below the medallion, the wall changes color and brick-mark pattern across a jagged x2048 seam; isolated brick outlines appear only on the right side.','futureRepairIntent':'Continue one approved wall material and existing brick placement across the join; retain the clipped forge glow.'},
  {'id':'c02-upper-eave-gold-step','kind':'material_seam','priority':2,'approximateTilePixelBox':[768,768,1280,1280],'patches':['p01_01','p01_02','p02_01','p02_02'],'evidence':['main-intersections.png'],'observation':'Gold eave face around x1024/y1024 has a visible irregular darker patch boundary within the same rim face.','futureRepairIntent':'Unify restrained gold highlight on the unchanged eave geometry.'},
  {'id':'c01-c02-external-continuity','kind':'external_tile_seam','priority':1,'boundary':'r09_c01:right / r09_c02:left','boundaryTileYPixels':[1024,4096],'evidence':['external-r09_c01-to-r09_c02.png'],'observation':'At the actual tile edge, row 2 gold/wood brightness steps abruptly. In row 3, a gold rectangular timber inset on c01 terminates exactly at the border while c02 continues a dark panel; beam grain/tones differ. Row 4 upper beam also has a straight tone step. All four edge segments were visually viewed; rows 1-2 still require geometry reconciliation.','futureRepairIntent':'Use a unified recorded native border across both tiles; preserve approved building geometry, including the gold inset and beam intersections.'}
 ],
 'r09_c03':[
  {'id':'c03-upper-gold-eave-tone','kind':'material_seam','priority':1,'approximateTilePixelBox':[1929,768,2167,1280],'patches':['p01_02','p01_03','p02_02','p02_03'],'evidence':['main-intersections.png','main-vertical-x2048.png'],'observation':'Upper curved gold eave has a conspicuous jagged warm-orange/light-gold split at x2048, through both upper lip and lower face.','futureRepairIntent':'Unify native gold tone/highlight without altering eave curvature or blue roof arrangement.'},
  {'id':'c03-paving-grout-jog','kind':'geometry_seam','priority':1,'approximateTilePixelBox':[1929,0,2167,500],'patches':['p01_02','p01_03'],'evidence':['main-vertical-x2048.png'],'observation':'Near the top x2048 corridor, blue-grey border and pale paving joints form small notches/doubled offsets where incoming diagonal seams should meet continuously.','futureRepairIntent':'Align only the existing grout/bevel line intersections at fixed street layout.'},
  {'id':'c03-metal-cylinder-tone','kind':'material_and_geometry_seam','priority':1,'approximateTilePixelBox':[2953,1929,3191,3072],'patches':['p02_03','p02_04','p03_03','p03_04'],'evidence':['main-intersections.png','main-vertical-x3072.png'],'observation':'Cylindrical metal surface has an irregular dark/light seam at x3072 through the top body and a stair-step highlight/band edge on the first horizontal gold hoop. Cylinder top/rim silhouette remains unresolved at the patch intersection.','futureRepairIntent':'Unify native metal sheen and hoop curve across the large clipped vessel, retaining original crop and scale.'},
  {'id':'c03-dense-stone-texture','kind':'material_contract_mismatch','priority':2,'approximateTilePixelBox':[2304,0,4096,2200],'patches':['p01_03','p01_04','p02_03','p02_04','p03_04'],'evidence':['main-intersections.png','main-vertical-x3072.png'],'observation':'Visible pale/blue-grey paving faces use dense cell-like mottling instead of the contracted quiet broad grey faces with sparse faint brush texture.','futureRepairIntent':'Quiet the native stone finish in a future verified-model repair while preserving slab joints and lighting.'},
  {'id':'c03-bottom-left-lighting','kind':'lighting_continuity_unresolved','priority':2,'approximateTilePixelBox':[256,2953,1920,3328],'patches':['p03_01','p03_02','p04_01','p04_02'],'evidence':['left4x2-horizontal-y3072.png','bottom-left-two-available-cores.png'],'observation':'The newly available bottom-left rectangle retains hard polygonal tone changes across the post and wall near y3072; native lighting/shadow continuity requires repair review. Window arch/lantern geometry was viewed in the two available bottom cores, but is not formally accepted.','futureRepairIntent':'Reconcile native timber illumination across row join without moving posts/window arch/lanterns.'},
  {'id':'c02-c03-external-continuity','kind':'external_tile_seam','priority':1,'boundary':'r09_c02:right / r09_c03:left','boundaryTileYPixels':[0,4096],'evidence':['external-r09_c02-to-r09_c03.png'],'observation':'All four actual edge segments were viewed. Row 1 masonry has a grout/bevel discontinuity near the lower horizontal joint. Row 3 gold/wood finish steps along the tile boundary. In row 4, patterned red cloth above the lantern abruptly stops at the edge and lantern paint/timber shading changes on a straight vertical line.','futureRepairIntent':'Create a unified future native border with the correct existing cloth, lantern and beam surfaces; no decorative invention.'},
  {'id':'c03-two-missing-cores','kind':'coverage_missing','priority':1,'missingPatchIds':['p04_03','p04_04'],'approximateTilePixelBox':[2048,3072,4096,4096],'evidence':[],'observation':'No selected native outputs exist for the lower-right two patches. No missing slots were filled and no 4096-square tile is claimed.','futureRepairIntent':'Resume these two native patches only after the explicit verified GPT Image 2.5 route is available.'}
 ]
}
policy_files=[Path('D:/work/image/AGENTS.md'),Path('D:/work/image/docs/IMAGE_MODEL_REQUIREMENT.md')]
summary={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'Southwest left lane current selected r09_c01/r09_c02/r09_c03 only',
 'status':'local_QA_finished_new_generation_paused_by_explicit_model_requirement',
 'policyEvidence':[{'file':str(p),'sha256':sha(p),'actuallyRead':True} for p in policy_files],
 'requestedImageModel':'GPT Image 2.5','verifiedImage25RouteAvailable':False,'newGeneratorCallsDuringThisLocalReview':0,
 'actualModel':None,'actualQuality':None,'paidApiUsed':False,'gitUsed':False,
 'selectedNativeCount':46,'fullCoverageCandidateCount':2,'formalAcceptedCount':0,
 'completeCityOr64TilesClaimed':False,'nativeQaPanelsBuilt':28,'nativeQaPanelsActuallyViewed':17,
 'writesRestrictedTo':'Southwest tile-local pipeline review folders','sharedProgressOrCatalogChanged':False,'tiles':[]}
for tile,names in viewed.items():
 q=SW/tile/'pipeline'/TAG
 m=read(q/'manifest.json')
 all_panels=[p for r in m['assembledRectangles'] for p in r['panels']]+m['qaImages']
 inspected=[];pending=[]
 for p in all_panels:
  entry={'file':p['file'],'sha256':p['sha256'],'pixels':p['pixels'],'status':'actually_viewed' if Path(p['file']).name in names else 'pending_not_viewed_in_this_review'}
  (inspected if entry['status']=='actually_viewed' else pending).append(entry)
 assert len(inspected)==len(names)
 report={'schemaVersion':1,'createdAtUtc':summary['createdAtUtc'],'tile':tile,'manifest':str(q/'manifest.json'),'manifestSha256':sha(q/'manifest.json'),
  'selectedNativeCount':m['selectedNativeCount'],'missingPatchIds':m['missingPatchIds'],'formalAccepted':False,
  'status':'defects_open_formal_acceptance_withheld','actualModel':None,'actualQuality':None,
  'sourceCandidateActuallyViewed':True,'sourceCandidateViewNote':'Full or partial overview viewed; per-pixel material acceptance is not established by overview.',
  'additionalRectangleActuallyViewed':tile=='r09_c03','actuallyViewedNativeQaPanels':inspected,
  'unreviewedNativeQaPanels':pending,'repairQueue':findings[tile],
  'externalBordersNotReviewed':['top','bottom']+(['left_outer_world_edge'] if tile=='r09_c01' else [])+(['right_to_unbuilt_r09_c04'] if tile=='r09_c03' else []),
  'modelGate':'No new generation or AI repair until explicit verified GPT Image 2.5 route exists. Existing art remains preserved and actual model metadata unknown.',
  'generatorCallsDuringReview':0,'sourceResampling':False,'missingPixelsFilled':False}
 out=q/'visual-review-and-repair-queue.json';assert not out.exists();out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 summary['tiles'].append({'tile':tile,'report':str(out),'reportSha256':sha(out),'selectedNativeCount':m['selectedNativeCount'],'missingPatchIds':m['missingPatchIds'],'viewedNativeQaPanelCount':len(inspected),'pendingNativeQaPanelCount':len(pending),'repairQueueCount':len(findings[tile]),'formalAccepted':False,'sourceOutputs':[{k:r[k] for k in ['file','sha256','pixels','rectangleInclusive']} for r in m['assembledRectangles']]})
out=SW/'r09_c03/pipeline/local-review-20261013-v01/left-lane-local-review-handoff.json'
assert not out.exists();out.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'report':str(out),'sha256':sha(out),'selectedNativeCount':46,'nativeQaPanelsActuallyViewed':17,'formalAcceptedCount':0,'tiles':summary['tiles']},ensure_ascii=False))
