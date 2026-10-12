from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
W=Path(__file__).resolve().parent;B=W.parent;sys.path.insert(0,str(B));from assemble_r03_c03 import minimum_vertical_seam
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def wr(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
base=read(W/'repair-v1/extended.assembly.json');a=np.asarray(Image.open(base['candidate']['file']).convert('RGB')).copy();ids=np.asarray(Image.open(base['sourceIdMap']['file'])).copy();sources=base['sources'];origin=base['globalCoreBox'][:2];out=W/'repair-v2';out.mkdir(exist_ok=True);qa=out/'qa';qa.mkdir(exist_ok=True);ops=[]
for name,rect,band in [('r04_c02_green_step_v01',[230,360,600,610],50),('r04_c02_red_cloth_whole_v01',[0,445,1000,900],60)]:
 p=B/'native'/(name+'.png');g=read(str(p)+'.generation.json');gb=g['globalNativeBox'];im=np.asarray(Image.open(p).convert('RGB'));x0,y0,x1,y1=rect;x=gb[0]-origin[0]+x0;y=gb[1]-origin[1]+y0;h=y1-y0;w=x1-x0;old=a[y:y+h,x:x+w].copy();inc=im[y0:y1,x0:x1];mi=ids[y:y+h,x:x+w];yy,xx=np.mgrid[:h,:w]
 wl,_=minimum_vertical_seam(old[:,:band],inc[:,:band]);er,_=minimum_vertical_seam(old[:,-band:],inc[:,-band:]);nt,_=minimum_vertical_seam(old[:band].transpose(1,0,2),inc[:band].transpose(1,0,2));st,_=minimum_vertical_seam(old[-band:].transpose(1,0,2),inc[-band:].transpose(1,0,2));m=(xx>=wl[:,None])&(xx<w-band+er[:,None])&(yy>=nt[None,:])&(yy<h-band+st[None,:])
 sid=max(s['sourceId'] for s in sources)+1;sources.append({'sourceId':sid,'file':str(p),'sha256':sha(p),'generationRecord':str(p)+'.generation.json','globalNativeBox':gb});sub=a[y:y+h,x:x+w];sub[m]=inc[m];mi[m]=sid
 full=np.zeros((1254,1254),np.uint8);full[y0:y1,x0:x1]=m*255;mp=out/(name+'.mask.png');Image.fromarray(full).save(mp)
 # Whole repair rectangle plus native context, four edges contained in the crop.
 bx=[max(0,x-100),max(0,y-100),min(a.shape[1],x+w+100),min(a.shape[0],y+h+100)];Image.fromarray(a[bx[1]:bx[3],bx[0]:bx[2]]).save(qa/(name+'.after.png'))
 ops.append({'native':str(p),'mask':str(mp),'maskSha256':sha(mp),'globalNativeBox':gb,'pixels':int(m.sum()),'rectangle':rect,'band':band})
for s in sources:
 yy,xx=np.where(ids==s['sourceId'])
 if not len(xx):continue
 gb=s['globalNativeBox'];im=np.asarray(Image.open(s['file']).convert('RGB'));assert np.array_equal(a[yy,xx],im[yy+origin[1]-gb[1],xx+origin[0]-gb[0]])
def save(ar,mi,name,box):
 pp=out/(name+'.png');ip=out/(name+'.source-id.png');Image.fromarray(ar).save(pp);Image.fromarray(mi).save(ip);used=set(map(int,np.unique(mi)));wr(out/(name+'.assembly.json'),{'candidate':{'file':str(pp),'sha256':sha(pp)},'sourceIdMap':{'file':str(ip),'sha256':sha(ip)},'globalCoreBox':box,'sources':[s for s in sources if s['sourceId'] in used],'proof':{'pixels':mi.size,'mismatches':0},'base':str(W/'repair-v1/extended.assembly.json'),'repairs':ops,'formalAccepted':False,'status':'candidate-pending-full-visual-review'})
save(a,ids,'extended',base['globalCoreBox']);core=a[115:4211,115:4211];save(core,ids[115:4211,115:4211],'r04_c02.candidate',[4096,12288,8192,16384]);pr=Image.fromarray(core);pr.thumbnail((1400,1400));pr.save(out/'overview.preview-only.jpg',quality=94)
for r in range(4):
 for c in range(4):Image.fromarray(core[r*1024:(r+1)*1024,c*1024:(c+1)*1024]).save(qa/f'core-{r+1}-{c+1}.png')
for j in range(1,4):
 for k in range(4):
  Image.fromarray(core[k*1024:(k+1)*1024,j*1024-240:j*1024+240]).save(qa/f'v{j}-{k+1}.png');Image.fromarray(core[j*1024-240:j*1024+240,k*1024:(k+1)*1024]).save(qa/f'h{j}-{k+1}.png')
for r in range(1,4):
 for c in range(1,4):Image.fromarray(core[r*1024-300:r*1024+300,c*1024-300:c*1024+300]).save(qa/f'junction-{r}-{c}.png')
for k in range(4):
 Image.fromarray(a[0:480,115+k*1024:115+(k+1)*1024]).save(qa/f'north-{k+1}.png');Image.fromarray(a[115+k*1024:115+(k+1)*1024,-480:]).save(qa/f'east-{k+1}.png')
wr(out/'operations.json',ops);print(json.dumps({'repairs':len(ops),'nativePixels':a.shape[0]*a.shape[1],'mismatches':0,'candidate':str(out/'r04_c02.candidate.png')}))
