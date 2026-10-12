from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *
s=read(ZONE/'selection-r05_c11.json');out=ZONE/'qa/r05_c11-recovery-stable-crosses';assert not out.exists();out.mkdir();entries=[]
for r in range(1,4):
 for c in range(2,4):
  a=Image.new('RGB',(512,512));src=[]
  for dr in [0,1]:
   for dc in [0,1]:
    ident=s['cores'][r-1+dr][c-1+dc];p=ZONE/'native'/f'{ident}.png';core=Image.open(p).crop((115,115,1139,1139));x=768 if dc==0 else 0;y=768 if dr==0 else 0;a.paste(core.crop((x,y,x+256,y+256)),(dc*256,dr*256));src.append({'id':ident,'sha256':sha(p)})
  p=out/f'cross-{r}-{c}-100pct.png';a.save(p);entries.append({'file':p.as_posix(),'sha256':sha(p),'sources':src,'status':'pending_visual_review'})
write(out/'provenance.json',{'tileId':'r05_c11','operation':'exact core-corner256 assembly no scaling','entries':entries})
print(out.as_posix())
