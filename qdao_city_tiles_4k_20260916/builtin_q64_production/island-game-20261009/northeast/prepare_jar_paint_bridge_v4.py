from native_work import *
ident='r04_c12_cross_01_02_jar_paint_repair_v4'
gp=ZONE/'guides'/f'{ident}.png';assert not gp.exists()
src=ZONE/'guides/r04_c12_cross_01_02_jar_paint_repair_v2.png';shutil.copy2(src,gp)
d=read(src.with_suffix('.png.derivation.json'))
for s in d['sources']:
 if s['sha256']=='0405a72d05a7e7cb6982dde405eb6aa1188079af02c77848bba5940f283292e1':s['file']=(ZONE/'qa/history/0405a72d05a7-r03_c12.png').as_posix()
write(gp.with_suffix('.png.derivation.json'),d);write(ZONE/'prompts'/f'{ident}.inputs.json',[{'file':gp.as_posix(),'sha256':sha(gp),'role':'only edit target; color and geometry authority, minimal color repair','derivationRecord':gp.with_suffix('.png.derivation.json').as_posix()}])
p=ZONE/'native/r04_c12_cross_01_02_jar_paint_repair_v3.png.generation.json';q=read(p);q.update(status='rejected_perimeter_color_shift',internalSeams='geometry continuous but output changes top/right attachment values');write(p,q)
print(gp.as_posix())

