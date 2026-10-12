from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *
i='r04_c11_cross_01_04_border_repair_v2';base=ZONE/'native/r04_c11_p01_04.png'; right=ZONE/'tiles/r04_c12.png'; upper=ZONE/'tiles/r03_c11.png';diagonal=ZONE/'tiles/r03_c12.png'
box=[44661,12173,45915,13427];out=Image.new('RGB',(1254,1254));sources=[]
for p,b in [(base,[43917,12173,45171,13427]),(right,[45056,12288,49152,16384]),(upper,[40960,8192,45056,12288]),(diagonal,[45056,8192,49152,12288])]:
 q=[max(box[0],b[0]),max(box[1],b[1]),min(box[2],b[2]),min(box[3],b[3])];crop=[q[0]-b[0],q[1]-b[1],q[2]-b[0],q[3]-b[1]];at=[q[0]-box[0],q[1]-box[1]];out.paste(Image.open(p).crop(crop),at);sources.append({'file':p.as_posix(),'sha256':sha(p),'sourceCrop':crop,'targetPaste':at})
p=ZONE/'guides'/f'{i}.png';assert not p.exists();out.save(p);write(p.with_suffix('.png.derivation.json'),{'operation':'exact native assembly straddling tile boundary; only western280x1024 core subcrop may be pasted into r04c11','sources':sources,'nativeWorldBox':box,'coreWorldBox':[44776,12288,45800,13312],'coreCrop':[115,115,1139,1139],'finalArt':False})
write(ZONE/'prompts'/f'{i}.inputs.json',[{'file':p.as_posix(),'sha256':sha(p),'role':'edit target; approved right area x395..1254 is fixed, repair only x115..395 left strip','derivationRecord':p.with_suffix('.png.derivation.json').as_posix()}])
