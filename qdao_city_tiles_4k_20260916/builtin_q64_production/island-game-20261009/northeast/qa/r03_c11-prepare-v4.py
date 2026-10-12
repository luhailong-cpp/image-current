from pathlib import Path
import sys,shutil
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *
i='r03_c11_cross_03_03_stair_return_repair_v3'; j='r03_c11_cross_03_03_stair_finish_v4'
src=ZONE/'native'/f'{i}.png';dst=ZONE/'guides'/f'{j}.png';assert not dst.exists();shutil.copy2(src,dst)
d=read(ZONE/'guides'/f'{i}.png.derivation.json');d.update(operation='exact native repair output used as next edit target, no resampling',editTargetSource={'file':src.as_posix(),'sha256':sha(src),'generationRecord':src.with_suffix('.png.generation.json').as_posix()});write(dst.with_suffix('.png.derivation.json'),d)
write(ZONE/'prompts'/f'{j}.inputs.json',[{'file':dst.as_posix(),'sha256':sha(dst),'role':'edit target, exact native1254 square; retain repaired square low-step end and repair only vertical stitching','derivationRecord':dst.with_suffix('.png.derivation.json').as_posix()}])
