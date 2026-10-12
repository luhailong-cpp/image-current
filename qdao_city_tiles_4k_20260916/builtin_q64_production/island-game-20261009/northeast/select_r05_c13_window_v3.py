from native_work import *
base=ZONE/'tiles/r05_c13.png';hist=ZONE/'qa/history/r05_c13-complete-48a92ae62ee6';hist.mkdir(exist_ok=True)
for p in [base,base.with_suffix('.png.derivation.json'),ZONE/'selection-r05_c13.json']:shutil.copy2(p,hist/p.name)
id='r05_c13_cross_03_window_repair_v3';p=ZONE/'qa'/f'{id}.overlay.json';rec=read(p);rec['review']='passed_native_full_and_four_perimeters';rec['finding']='central window foliage cut and full counter split removed; no visible new discontinuity at four core boundaries';write(p,rec)
s=read(ZONE/'selection-r05_c13.json');s['overlays'].append(id);s['updatedAtUtc']=now();write(ZONE/'selection-r05_c13.json',s)

