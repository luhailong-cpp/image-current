from workflow import *
from PIL import Image
import numpy as np,sys
tid='r12_c12';q=read(ROOT/'selected-native-r11_c12-repaired-v02.json');ids=np.asarray(Image.open(q['sourceIdMap']));sources={s['id']:s for s in q['sources']};base=np.asarray(Image.open(q['candidate']).convert('RGB'))
for col in [1,4]:
 pid=f'{tid}_p1{col}';p=patch(pid);xb=p['nativeGlobalBox'][0]-11*4096;guide=np.asarray(Image.open(ROOT/'guides'/f'{pid}.layout-only.png').convert('RGB')).copy();contributors={}
 for x in range(1254):
  tx=xb+x
  if not 0<=tx<4096:continue
  for y in range(230):
   ty=3981+y
   if ty<4096:guide[y,x]=base[ty,tx];continue
   sid=int(ids[4095,tx]);s=sources[sid]
   if sid not in contributors:contributors[sid]=np.asarray(Image.open(s['file']).convert('RGB'))
   a=contributors[sid];ox,oy=s['tileToNativeOffset'];nx,ny=tx+ox,ty+oy
   if 0<=nx<1254 and 0<=ny<1254:guide[y,x]=a[ny,nx]
 out=ROOT/'guides'/f'{pid}.native-context-v02.png';assert not out.exists();Image.fromarray(guide).save(out)
 write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'nativeGlobalBox':p['nativeGlobalBox'],'operation':'Actual candidate north115 rows plus each matching selected native south halo at unchanged world coordinates. Guide only.','candidate':q['candidate'],'candidateSha256':q['sha256'],'nativeSourcesUsed':[sources[s] for s in contributors],'usableAsFinalArt':False})
print('top230 true native guides for p12/p13')

