from native_work import *
tid='r05_c13';tile=ZONE/'tiles'/f'{tid}.png';qa=ZONE/'qa'/f'{tid}-final'
items=[dict(file=p.as_posix(),sha256=sha(p),status='passed_visual_100_percent') for p in sorted(qa.glob('*100pct.png'))]
assert len(items)==49
record=dict(tileId=tid,file=tile.as_posix(),sha256=sha(tile),reviewedAtUtc=now(),status='passed_internal49_and_upper_full_border',coreCount=16,internalSeamCount=24,crossCount=9,items=items,reviewMethod='All49 native crops viewed, then changed3 cores and8 seam/cross crops rechecked after final window and shared-beam repairs; all repair external perimeters separately viewed at native scale.',repairs=['r05_c13_cross_02_03_gold_repair_v2','r05_c13_cross_02_01_repair','r05_c13_cross_03_window_repair_v3','r05_c13_cross_left_p01_beam_repair-r05_c13'],findingsResolved=['gold eave height step','gray wall rectangular tone discontinuity','window foliage cut and central counter offset','left shared thin red beam floating end and gold fascia mismatch'],outerEdges=dict(upper='passed_complete4096 boundary against r04_c13, four1024 segments at100%',left='p01 shared repair passed full surrounding and internal join; p02-p04 native anchors previously passed; pending full c12 tile assembly review',right='pending adjacent c14 completion; rightmost selected native anchors unchanged',bottom='pending adjacent r06 tile'),formalAccepted=False,finalArtUpscaled=False,actualModel=None,actualQuality=None)
write(ZONE/'qa'/f'{tid}-round2-acceptance.json',record)
p=ZONE/'qa/r05_c13-upper-border-round2/record.json';r=read(p);r['review']='passed_all_four_native1024_segments';r['reviewedAtUtc']=now();write(p,r)
p=tile.with_suffix('.png.derivation.json');r=read(p);r['internalReview']='passed16core24seam9cross';r['status']='complete_internal_QA_passed_external_assembly_pending';r['externalSeams']=record['outerEdges'];r['acceptanceRecord']=(ZONE/'qa'/f'{tid}-round2-acceptance.json').as_posix();write(p,r)
p=ZONE/'selection-r05_c13.json';s=read(p)
for issue in s.get('pendingIssues',[]):issue['status']='resolved_native_repair_visual_passed';issue['resolvedAtUtc']=now()
s['pendingIssues']=[];s['resolvedIssues']=r.get('resolvedIssues',record['findingsResolved']);s['internalReview']='passed16core24seam9cross';s['formalAccepted']=False;s['updatedAtUtc']=now();write(p,s)
for ident in [x for row in s['cores'] for x in row]:
 p=ZONE/'native'/f'{ident}.png.generation.json';r=read(p);r['status']='selected_in_internally_reviewed_complete_tile';r['assembledTileReview']=record['sha256'];r['note']='Native core selected with recorded repair overlays where required; this status does not imply raw native candidate individually seamless without overlays.';write(p,r)
print(sha(tile))

