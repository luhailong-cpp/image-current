from workflow import ROOT,read,write,now,sha
q=ROOT/'qa/capacity-gate/r11_c12-partial/index.json';d=read(q)
d.update(reviewedAt=now(),reviewer='root',reviewStatus='existing13_seams_and4_junctions_major_geometry_pass',scopeLimit='Only10existingcores; missing6cores, unknown remaining edges; not whole4K or formal acceptance.')
for e in d['entries']:e.update(status='visual_review_no_obvious_major_contour_discontinuity',reviewer='root')
d['observations']=['All17 samples inspected at native resolution. Stone joints, railing contours, lantern frame and paper planes remain continuous across sampled cuts.','Minor texture and daylight variations remain; judge them with the complete4K sample after6missingcores exist.','No generated artwork, blending, sharpening, new coordinates or deletion during capacity gate.']
write(q,d)
p=ROOT/'qa/capacity-gate/risk-and-readiness-summary.json';s=read(p);s.update(partialR11Review=str(q.relative_to(ROOT)),partialR11SeamsReviewed=13,partialR11JunctionsReviewed=4,updatedAt=now());write(p,s)
p=ROOT/'capacity-gate-ack.json';s=read(p);s.update(allowedWorkStatus='inventory_root_source_replay_existing_border_and_partial_art_QA_completed',updatedAtUtc=now(),newArtworkCallsAfterGate=0,partialR11Review='qa/capacity-gate/r11_c12-partial/index.json');write(p,s)
print({'r11partialSeamsReviewed':13,'junctionsReviewed':4,'gate':'still active, not released by worker'})
