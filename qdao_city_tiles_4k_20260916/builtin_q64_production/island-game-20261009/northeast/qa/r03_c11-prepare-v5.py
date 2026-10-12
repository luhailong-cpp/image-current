from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *
i='r03_c11_cross_03_03_stair_finish_v4';j='r03_c11_cross_03_03_stair_finish_v5'
src=ZONE/'native'/f'{i}.png';original=ZONE/'guides/r03_c11_cross_03_03_stair_paving_repair.png';dst=ZONE/'guides'/f'{j}.png';assert not dst.exists()
im=Image.open(src).convert('RGB');o=Image.open(original).convert('RGB')
for box in [(0,0,1254,230),(0,1024,1254,1254),(0,0,230,1254),(1024,0,1254,1254)]:im.paste(o.crop(box),(box[0],box[1]))
im.save(dst);d=read(ZONE/'guides'/f'{i}.png.derivation.json');d.update(operation='mechanical exact native repair interior with four230px original native outer anchor strips; no resampling',editTargetSource={'file':src.as_posix(),'sha256':sha(src)},originalPerimeter={'file':original.as_posix(),'sha256':sha(original),'strips':[[0,0,1254,230],[0,1024,1254,1254],[0,0,230,1254],[1024,0,1254,1254]]});write(dst.with_suffix('.png.derivation.json'),d)
write(ZONE/'prompts'/f'{j}.inputs.json',[{'file':dst.as_posix(),'sha256':sha(dst),'role':'edit target: final native interior repair with exact original four230px perimeter anchor bands; preserve outer bands','derivationRecord':dst.with_suffix('.png.derivation.json').as_posix()}])
