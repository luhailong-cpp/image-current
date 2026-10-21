import sys
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
import west_sol as w
p='r07_c11_p34';src=w.Z/f'native/{p}-v3-west_sol.png'
w.write(w.R/f'{p}-v3.review.json',dict(native=w.ref(src),reviewedAtUtc=w.now(),status='best_candidate_not_passed',selectedLocallyForProposal=True,formalAccepted=False,issues=[dict(location='right core seam world x45056 near y27640..27763',description='Blue mooring bollard cap and stave boundaries retain a small step against r07_c12_p31-v1; v3 substantially reduced v2 height error but not yet pass',propagationConstraint='Do not generate p44 using this bottom anchor; p13 independent and left230 of this image excludes issue')],wholeTile49Pending=True))
sel=w.own_selection('r07_c11');sel[p]=dict(**w.ref(src),reviewStatus='best_candidate_not_passed',blockedPropagation='bottom bollard; skip p44')
w.write(w.R/'r07_c11.selected.json',sel,True)
print('3 local candidates; p34 pending right bollard seam')

