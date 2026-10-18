from native_work import *
ident='r06_c14_p04_02'
record=ZONE/'native'/f'{ident}.png.generation.json'
d=read(record);d.update(status='candidate_selected_pending_local_repair',internalSeams='pending_local_material_repair',reviewedAtUtc=now(),reviewNote='Top and left actual core joins continuous, but left anchor-to-interior transition at native x230 has visible vertical flower/leaf clipping, particularly y230-430. Repair after missing cores; right anchor unaffected.')
write(record,d)
s=ZONE/'selection-r06_c14.json';sel=read(s);sel['cores'][3][1]=ident;sel['updatedAtUtc']=now();write(s,sel)
write(ZONE/'qa'/f'{ident}.review.json',{'id':ident,'sha256':sha(ZONE/'native'/f'{ident}.png'),'status':'requires_native_local_repair','issue':'Vertical cut at native x230, most visible y230-430, inside core; does not propagate to right border.','repairPlanned':True,'formalAccepted':False,'reviewedAtUtc':now()})
print('Provisional selected; local defect remains unpassed')
