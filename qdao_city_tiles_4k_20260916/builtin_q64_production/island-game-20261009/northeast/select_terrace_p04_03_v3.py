from native_work import *
import shutil
tid='r03_c13'; p=ZONE/'tiles'/f'{tid}.png'; oldhash=sha(p)
archive=ZONE/'qa'/'history';archive.mkdir(exist_ok=True)
for src in [p,p.with_suffix('.png.derivation.json'),ZONE/'qa'/f'{tid}-whole-review.json',ZONE/f'selection-{tid}.json']:
 dst=archive/(oldhash[:12]+'-'+src.name)
 if not dst.exists():shutil.copy2(src,dst)
s=read(ZONE/f'selection-{tid}.json');s['cores'][3][2]='r03_c13_p04_03_v3';write(ZONE/f'selection-{tid}.json',s)
rec=read(ZONE/'native/r03_c13_p04_03_v2.png.generation.json');rec.update(status='superseded_geometry_failure',supersededBy='r03_c13_p04_03_v3');write(ZONE/'native/r03_c13_p04_03_v2.png.generation.json',rec)
gpath=ZONE/'guides/r03_c13_cross_terrace_repair.png.derivation.json';g=read(gpath);g['source']['archivedSnapshot']=(archive/(oldhash[:12]+'-'+p.name)).as_posix();g['source']['archivedDerivationRecord']=(archive/(oldhash[:12]+'-'+p.with_suffix('.png.derivation.json').name)).as_posix();write(gpath,g)
print(oldhash)

