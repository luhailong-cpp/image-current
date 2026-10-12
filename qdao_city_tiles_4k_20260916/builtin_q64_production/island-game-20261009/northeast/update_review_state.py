from native_work import *
overlay=ZONE/'qa/r03_c12_cross_02_02_repair.overlay.json'; q=read(overlay); q['review']='passed_internal_geometry_color_and_four_edges'; q['reviewedAtUtc']=now(); q['reviewerEvidence']='root direct 100% inspection plus independent contract_review'; write(overlay,q)
for ident in ['r03_c12_p03_02','r03_c12_p03_03_v2']:
    p=ZONE/'native'/f'{ident}.png.generation.json'; q=read(p); q['status']='usable_native_with_required_overlay'; q['requiredOverlay']=overlay.as_posix(); write(p,q)
p=ZONE/'native/r03_c12_cross_02_02_repair.png.generation.json'; q=read(p); q['status']='usable_native_repair_overlay'; q['internalSeams']='four overlay perimeter edges passed'; write(p,q)
p=ZONE/'native/r03_c12_p03_03.png.generation.json'; q=read(p); q['status']='rejected_superseded_by_repair'; q['supersededBy']=(ZONE/'native/r03_c12_p03_03_v2.png.generation.json').as_posix(); write(p,q)
p=ZONE/'native/r03_c12_p03_04.png.generation.json'; q=read(p); q['status']='candidate_geometry_repair_required'; q['defect']='cropped wine-vessel neck at x230 y160..400'; write(p,q)
p=ZONE/'progress.json'; q=read(p); q['usableNativeCount']=sum(read(p)['status'].startswith(('usable_native','usable_seed')) for p in (ZONE/'native').glob('*.png.generation.json')); q['usableCorePatchCount']=11; q['usableRepairOverlayCount']=1; q['nextStep']='repair wine-vessel neck on p03_04, then finish bottom row'; q['updatedAtUtc']=now(); write(p,q)
ident='r03_c12_p03_04_v2'; refs=[]
for f,role in zip(['native/r03_c12_p03_04.png','native/r03_c12_p03_03_v2.png',read(ZONE/'reference-audit.json')['references'][1]['file'],read(ZONE/'reference-audit.json')['references'][2]['file']],['edit target: native patch with cut vessel neck','left native reference; required wall-base overlay does not intersect this right-edge anchor','approved material style','primary approved Daoist Q style']):
    p=ZONE/f if not Path(f).is_absolute() else Path(f); refs.append({'file':p.as_posix(),'sha256':sha(p),'role':role})
write(ZONE/'prompts'/f'{ident}.inputs.json',refs)
