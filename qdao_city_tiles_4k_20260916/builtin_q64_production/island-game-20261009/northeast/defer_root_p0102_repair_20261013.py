from native_work import *
ident='r03_c09_cross_p0102_right_repair';ip=ZONE/'qa'/f'{ident}-inspection/inspection.json';d=read(ip)
for e in d['inspectionImages']:
 if any('/'+n+'-100pct.png' in e['file'].replace('\\','/') for n in ['left','right','top-halo-context','bottom-halo-context']):
  e.update(status='failed_contour_continuity',reviewer='root')
d.update(status='unselected_failed_overlay_boundaries',reviewedAtUtc=now(),finding='Central grout improved, but all four pasted core edges introduce new offsets/material discontinuity. Second attempt unsuccessful; do not apply overlay. Continue independent cores, defer concentrated repair.');write(ip,d)
for ident in ['r03_c09_cross_p0102_right_repair','r03_c09_p01_02_v2']:
 p=ZONE/'native'/f'{ident}.png.generation.json';r=read(p);r.update(status='unselected_failed_overlay_boundaries' if '_cross_' in ident else 'selected_best_candidate_pending_right_join_repair',internalSeams='NOT PASSED: grout contour displacement; 2 unsuccessful repair attempts recorded.');write(p,r)
p=ZONE/'selection-r03_c09.json';s=read(p);s['cores'][0][1]='r03_c09_p01_02_v2';s.update(updatedAtUtc=now(),internalReview='partial_coverage_with_pending_right_join_issue',pendingIssues=['p01_02_v2 to p01_03 right grout contour offsets. Two repair attempts unsuccessful; centered overlay is unselected. Best native candidate retained, issue not passed.']);write(p,s)
print('Saved best p01_02_v2 with unresolved seam; rejected overlay preserved; next independent p01_01')

