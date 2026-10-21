from native_work import *
ident='r03_c09_p01_02'
p=ZONE/'qa'/f'{ident}__r03_c09_p01_03.json';d=read(p);d.update(status='failed_geometry_continuity',reviewer='root',reviewedAtUtc=now(),finding='Diagonal slab edge shifts at exact core join, visible near joined image y210 and y550. Not selected; repair v2 prepared.');write(p,d)
p=ZONE/'native'/f'{ident}.png.generation.json';d=read(p);d.update(status='unselected_requires_right_join_repair',internalSeams='failed right grout contour continuity');write(p,d)
p=ZONE/'prompts/r03_c09_p01_02_v2.inputs.json';d=read(p);d[0]['role']='edit target: prior native candidate with exact right overlap replaced; entire image native detail';d[1]['role']='exact native RIGHT neighbor';write(p,d)

