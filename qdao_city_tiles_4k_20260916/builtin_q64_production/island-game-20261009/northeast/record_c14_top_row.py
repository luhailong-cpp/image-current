from native_work import *
ids=['r05_c14_p01_01','r05_c14_p01_02','r05_c14_p01_03_v2','r05_c14_p01_04']
for ident in ids:
 p=ZONE/'qa'/f'cross_{ident}.json';q=read(p);q.update(status='passed_visual_review_1to1',reviewer='root',reviewedAtUtc=now());write(p,q)
p=ZONE/'native/r05_c14_p01_03.png.generation.json';q=read(p);q.update(status='rejected_internal_straight_crop_edge',supersededBy='r05_c14_p01_03_v2',finding='Cliff left contour had a ruler-straight pasted edge; version2 corrected it and joins passed.');write(p,q)
p=ZONE/'receipts/r05_c14_p01_03.attempt-01.error.json';q=read(p);q.update(resolved=True,recovery='one same-input builtin retry succeeded; saved r05_c14_p01_03 native then geometry-corrected with v2',successfulReceipt=str(ZONE/'receipts/r05_c14_p01_03.tool.json'));write(p,q)
write(ZONE/'qa/r05_c14-top-row-review.json',{'reviewedAtUtc':now(),'status':'passed_top_row_4cores_available_upper_left_joins_and4crossings','ids':ids,'hashes':{i:sha(ZONE/'native'/f'{i}.png') for i in ids},'scope':'first row only; remaining12cores absent','formalAccepted':False,'reviewer':'root','actualModel':None,'actualQuality':None})

