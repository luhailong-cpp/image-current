from pathlib import Path
from PIL import Image
from workflow import ROOT,read,write,sha,now
src=ROOT/'tiles/r11_c12.partial-10of16.png';im=Image.open(src).convert('RGBA');sel=read(ROOT/'selection-r11_c12.json')['patchVersions']
q=ROOT/'qa/capacity-gate/r11_c12-partial';q.mkdir(exist_ok=True);entries=[]
def crop(name,box,kind):
 a=im.crop(box);assert a.getchannel('A').getextrema()==(255,255)
 p=q/f'{name}.png';a.convert('RGB').save(p)
 entries.append({'id':name,'kind':kind,'file':str(p),'sha256':sha(p),'source':str(src),'sourceSha256':sha(src),'sourceCrop':box,'operation':'exact original-pixel crop from partial mechanical assembly; all pixels within sample have source coverage','status':'pending_visual_review'})
for r in range(1,5):
 for c in range(1,4):
  if f'{r}{c}' in sel and f'{r}{c+1}' in sel:crop(f'h{r}{c}',[c*1024-256,(r-1)*1024,c*1024+256,r*1024],'horizontal_neighbor')
for r in range(1,4):
 for c in range(1,5):
  if f'{r}{c}' in sel and f'{r+1}{c}' in sel:crop(f'v{r}{c}',[(c-1)*1024,r*1024-256,c*1024,r*1024+256],'vertical_neighbor')
for r in range(1,4):
 for c in range(1,4):
  if all(f'{rr}{cc}' in sel for rr in [r,r+1] for cc in [c,c+1]):crop(f'j{r}{c}',[c*1024-256,r*1024-256,c*1024+256,r*1024+256],'four_patch_junction')
write(q/'index.json',{'createdAt':now(),'partialCoverage':True,'tile':'r11_c12','entries':entries,'formalAccepted':False})
print({'count':len(entries),'ids':[e['id'] for e in entries]})
