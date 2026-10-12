from pathlib import Path
from PIL import Image
import sys,os,runpy
os.environ['ISLAND_PROGRESS_FILE']='progress-r12_c11.json'
from workflow import ROOT,read,write,sha,patch,now
rc,version,desc=sys.argv[1:4];r,c=map(int,rc);pid='r12_c11_p'+rc
p=patch(pid);box=p['nativeGlobalBox'];guide=ROOT/'guides'/f'{pid}.native-context-{version}.png'
assert not (ROOT/'native'/f'{pid}_{version}.png').exists(),'Never regenerate existing native'
assert not guide.exists(),'Preserve guide; choose new version'
base=ROOT/'guides'/f'{pid}.layout-only.png';im=Image.open(base).convert('RGB');sources=[];placements=[]
def paste(file,nb,role):
 file=Path(file);src=Image.open(file).convert('RGB')
 inter=[max(box[0],nb[0]),max(box[1],nb[1]),min(box[2],nb[2]),min(box[3],nb[3])]
 if inter[2]<=inter[0] or inter[3]<=inter[1]:return
 crop=[inter[0]-nb[0],inter[1]-nb[1],inter[2]-nb[0],inter[3]-nb[1]];dest=[inter[0]-box[0],inter[1]-box[1]]
 im.paste(src.crop(crop),tuple(dest));sources.append({'file':str(file),'sha256':sha(file),'role':role});placements.append({'source':str(file),'sourceCrop':crop,'destination':dest,'globalIntersection':inter})
def native(file,role):
 file=Path(file);rec=read(Path(str(file)+'.generation.json'));assert [rec['width'],rec['height']]==[1254,1254];paste(file,rec['coordinate']['nativeGlobalBox'],role)
if r==1:
 for key,ver in {'41':'v02','42':'v01','43':'v02','44':'v01'}.items():native(ROOT/'native'/f'r11_c11_p{key}_{ver}.png','north accepted native full 230 halo')
 paste(ROOT/'tiles'/'r11_c11.candidate-v02.png',[40960,40960,45056,45056],'north accepted candidate exact core authority')
if c==4:
 approved=read(ROOT/'r12_c11-east-approved.json')
 for key,ver in approved.items():native(ROOT/'native'/f'r12_c12_p{key}_{ver}.png','east parent approved native halo')
selection=read(ROOT/'selection-r12_c11.json')
for nr,nc in [(r-1,c),(r,c+1),(r,c-1),(r+1,c)]:
 key=str(nr)+str(nc)
 if key in selection['patchVersions']:native(ROOT/'native'/f'r12_c11_p{key}_{selection["patchVersions"][key]}.png','selected adjacent native overlap')
im.save(guide);write(Path(str(guide)+'.generation.json'),{'file':str(guide),'sha256':sha(guide),'generatedAt':now(),'operation':'Unscaled exact native overlap and candidate border on layout-only guide; reference only','usableAsFinalArt':False,'base':str(base),'baseSha256':sha(base),'derivedFrom':sources,'placements':placements,'globalBox':box})
sys.argv=['r10_c11_request.py',pid,version,desc];runpy.run_path(str(ROOT/'r10_c11_request.py'),run_name='__main__')
