from native_work import *
p=ZONE/'qa/connected-area/r03-r04_c12-c13.json';q=read(p);q.update(status='shared_edges_and_center_passed_two_existing_internal_color_bands_pending',reviewer='root',reviewedAtUtc=now(),centerReview='passed_visual_100pct',pendingInternalDefects=['r03_c12/r03_c13 gold gourd horizontal tone band around localy2048','r03_c12 slender bottle horizontal tone band around localy3072'])
for s in q['seamEvidence']:
 s['status']='passed_visual_100pct' if s['pair']!=['r03_c12','r03_c13'] else 'previous_shared_edge_pass_retained_pending_internal_gourd_patch';s['sha256']=sha(s['file'])
write(p,q)
p=ZONE/'qa/connected-area/partial-group.json';q=read(p);q.update(status='passed_shared_north_and_west_r04_c14',reviewer='root',reviewedAtUtc=now())
for s in q['seamEvidence']:s.update(status='passed_visual_100pct',sha256=sha(s['file']))
write(ZONE/'qa/r04_c14-root-north-west-full-edges.json',q)
for tid in ['r03_c12','r03_c13']:
 p=ZONE/'tiles'/f'{tid}.png.derivation.json';d=read(p);d['internalReview']='pending local color band repair found in group preview';d['status']='native_complete_coverage_color_repair_pending';d['pendingColorRepair']='gold gourd and slender bottle' if tid=='r03_c12' else 'gold gourd';write(p,d)
print('saved full-edge passes and specific outstanding color repairs')

