from native_work import *
id='r05_c13_cross_left_p01_beam_repair'
for tile in ['r05_c12','r05_c13']:
 p=ZONE/'qa'/f'{id}-{tile}.overlay.json';r=read(p);r['review']='passed_shared_native_full_four_perimeters_and_internal_join';r['reviewedAtUtc']=now();r['finding']='thin red trim supported behind front post, gold fascia coherent, four external native joins visually continuous';write(p,r)
base=ZONE/'tiles/r05_c13.png';hist=ZONE/'qa/history/r05_c13-complete-92a523d470da';hist.mkdir(exist_ok=True)
for p in [base,base.with_suffix('.png.derivation.json'),ZONE/'selection-r05_c13.json']:shutil.copy2(p,hist/p.name)
p=ZONE/'selection-r05_c13.json';s=read(p);s['overlays'].append(id+'-r05_c13');s['updatedAtUtc']=now();write(p,s)

