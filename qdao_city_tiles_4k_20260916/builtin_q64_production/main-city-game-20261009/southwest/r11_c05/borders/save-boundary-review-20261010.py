from pathlib import Path
import json,hashlib
root=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest')
qa=root/'r11_c05'/'qa'/'boundary-review-20261010'
borders=root/'r11_c05'/'borders'
record=json.loads((borders/'r11-p01.north-fixed.context.border.json').read_text(encoding='utf-8'))
path=root/'r10_c05'/'repairs'/'output'/'r10_c05.repaired.candidate.png'
sha=hashlib.sha256(path.read_bytes()).hexdigest()
assert sha=='f228d0e07c4ed329bdcce87a46abb0ddeb48c9688dab1d86b33456051797ecad'
report={
 'status':'reject_for_visual_adoption',
 'recommendedForCurrentSelection':False,
 'formalAccepted':False,
 'reviewedAt':'2026-10-10',
 'visualMethod':'Viewed pixel-preserving before/after 1024x800 crops for all four columns, full 4096x800 boundary crop, and each 512x1024 internal seam crop.',
 'mechanicalPassed':True,
 'r10FinalSha256Unchanged':sha,
 'fixedContext':record['output'],
 'seamYInContextInclusive':[record['composition']['seamMin'],record['composition']['seamMax']],
 'seamYInR11CoreInclusive':[record['composition']['seamMin']-115,record['composition']['seamMax']-115],
 'findings':[
  {'priority':'P2','region':'r11 core x 0-520, top 114 rows','description':'Leaf shapes at the actual r10/r11 boundary now follow original r10 pixels. The local color transition is moved down into the leaf mass; mechanical ownership alone does not establish material continuity. No obvious leaf geometry break remains at row zero.'},
  {'priority':'P1','region':'r11 core x approximately 520-4096, top 114 rows','description':'North fixing introduces a conspicuous irregular lighter/darker tonal strip across the parapet and nearly the full first stair riser. The seam reads as an artificial wavy/polygon boundary. It is visibly worse than the straight tile-boundary tone transition in the original assembly.'},
  {'priority':'P2','region':'internal patch boundary x approximately 1024, stair risers throughout first native row','description':'Warm left / cooler right stone tones create irregular vertical transition areas; unchanged below core row 114.'},
  {'priority':'P3','region':'internal patch boundary x approximately 2048','description':'Milder color/texture transition remains, without clear step misalignment.'},
  {'priority':'P2','region':'internal patch boundary x approximately 3072; visible riser bands near core y 125-235, 333-445, 560-670, 790-900','description':'Distinct slanted polygonal warm/cool transitions remain. Geometry is aligned; stone shading and texture differ.'}
 ],
 'recommendation':'Keep the original selected r11 assembly. Retain this fixed context only as mechanical experiment/provenance. Perform geometry-locked image edits matching stone tone and texture across the north overlap and adjacent native patches, then rerun border composition and visual QA. Do not solve the visible mismatch with wider blur/feather or color adjustment.',
 'writesRestrictedTo':['r11_c05/borders','r11_c05/qa/boundary-review-20261010'],
 'generatedAiImages':0,
 'resizedArt':False,
 'selectionModified':False,
 'progressModified':False,
 'generationRecordsModified':False,
 'currentFormalArtModified':False
}
(qa/'visual-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'report':str(qa/'visual-review.json'),'northSeamCoreRange':report['seamYInR11CoreInclusive'],'fixedContextSha256':record['output']['sha256'],'r10Unchanged':True},ensure_ascii=False,indent=2))
