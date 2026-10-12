from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *
s=read(ZONE/'selection-r05_c11.json');out=ZONE/'qa/r05_c11-recovery-stable-boundaries';assert not out.exists();out.mkdir();entries=[]
for side,tid in [('top','r04_c11'),('right','r05_c12')]:
 ns=read(ZONE/f'selection-{tid}.json');np=Path(ns.get('candidatePath',ZONE/'tiles'/f'{tid}.png'));ni=Image.open(np)
 for k in range(4):
  ident=s['cores'][0][k] if side=='top' else s['cores'][k][3];p=ZONE/'native'/f'{ident}.png';core=Image.open(p).crop((115,115,1139,1139))
  if side=='top':
   patch=Image.new('RGB',(1024,512));patch.paste(ni.crop((k*1024,3840,(k+1)*1024,4096)),(0,0));patch.paste(core.crop((0,0,1024,256)),(0,256))
  else:
   patch=Image.new('RGB',(512,1024));patch.paste(core.crop((768,0,1024,1024)),(0,0));patch.paste(ni.crop((0,k*1024,256,(k+1)*1024)),(256,0))
  dst=out/f'{side}-{k+1}-100pct.png';patch.save(dst);entries.append({'file':dst.as_posix(),'sha256':sha(dst),'nativeId':ident,'nativeSha256':sha(p),'neighbor':np.as_posix(),'neighborSha256':sha(np),'status':'pending_visual_review'})
write(out/'provenance.json',{'tileId':'r05_c11','operation':'exact native256 strips no scaling','entries':entries})
