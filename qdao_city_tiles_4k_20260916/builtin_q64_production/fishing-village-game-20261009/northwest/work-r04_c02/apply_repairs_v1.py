from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
W=Path(__file__).resolve().parent;B=W.parent;sys.path.insert(0,str(B));from assemble_r03_c03 import minimum_vertical_seam
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def wr(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
base=read(W/'base-v1/extended.assembly.json');a=np.asarray(Image.open(base['candidate']['file']).convert('RGB')).copy();ids=np.asarray(Image.open(base['sourceIdMap']['file'])).copy();sources=base['sources'];origin=base['globalCoreBox'][:2];out=W/'repair-v1';out.mkdir(exist_ok=True);qa=out/'qa';qa.mkdir(exist_ok=True);ops=[]
items=[('r04_c02_green_hem_whole_v01',[70,430,1254,1254],110),('r04_c02_green_hem_post_v01',[0,400,1254,1254],110),('r04_c02_rope_joint_whole_v01',[0,0,1254,1254],80)]
for name,rect,band in items:
 p=B/'native'/(name+'.png');g=read(str(p)+'.generation.json');gb=g['globalNativeBox'];im=np.asarray(Image.open(p).convert('RGB'));x=gb[0]-origin[0];y=gb[1]-origin[1];old=a[y:y+1254,x:x+1254].copy();oi=ids[y:y+1254,x:x+1254]
 x0,y0,x1,y1=rect;aa=old[y0:y1,x0:x1];bb=im[y0:y1,x0:x1];h,w=aa.shape[:2];yy,xx=np.mgrid[:h,:w]
 wl,_=minimum_vertical_seam(aa[:,:band],bb[:,:band]);er,_=minimum_vertical_seam(aa[:,-band:],bb[:,-band:]);nt,_=minimum_vertical_seam(aa[:band].transpose(1,0,2),bb[:band].transpose(1,0,2));st,_=minimum_vertical_seam(aa[-band:].transpose(1,0,2),bb[-band:].transpose(1,0,2))
 local=(xx>=wl[:,None])&(xx<w-band+er[:,None])&(yy>=nt[None,:])&(yy<h-band+st[None,:]);m=np.zeros((1254,1254),bool);m[y0:y1,x0:x1]=local
 sid=max(s['sourceId'] for s in sources)+1;sources.append({'sourceId':sid,'file':str(p),'sha256':sha(p),'generationRecord':str(p)+'.generation.json','globalNativeBox':gb})
 sub=a[y:y+1254,x:x+1254];sub[m]=im[m];oi[m]=sid;mp=out/(name+'.mask.png');Image.fromarray((m*255).astype(np.uint8)).save(mp);Image.fromarray(sub).save(qa/(name+'.after.png'))
 # Edge strips displayed at exact native resolution, no resizing.
 for label,box in [('north',(0,0,1254,420)),('south',(0,834,1254,1254)),('west',(0,0,420,1254)),('east',(834,0,1254,1254))]:Image.fromarray(sub).crop(box).save(qa/(name+'.'+label+'.png'))
 ops.append({'native':str(p),'mask':str(mp),'maskSha256':sha(mp),'globalNativeBox':gb,'pixels':int(m.sum()),'rectangle':rect,'band':band})
for s in sources:
 yy,xx=np.where(ids==s['sourceId'])
 if not len(xx):continue
 gb=s['globalNativeBox'];im=np.asarray(Image.open(s['file']).convert('RGB'));assert np.array_equal(a[yy,xx],im[yy+origin[1]-gb[1],xx+origin[0]-gb[0]])
def save(ar,mi,name,box):
 pp=out/(name+'.png');ip=out/(name+'.source-id.png');Image.fromarray(ar).save(pp);Image.fromarray(mi).save(ip)
 used=set(map(int,np.unique(mi)));wr(out/(name+'.assembly.json'),{'candidate':{'file':str(pp),'sha256':sha(pp)},'sourceIdMap':{'file':str(ip),'sha256':sha(ip)},'globalCoreBox':box,'sources':[s for s in sources if s['sourceId'] in used],'proof':{'pixels':mi.size,'mismatches':0},'repairs':ops,'formalAccepted':False,'status':'candidate-pending-full-visual-review'})
save(a,ids,'extended',base['globalCoreBox']);core=a[115:4211,115:4211];save(core,ids[115:4211,115:4211],'r04_c02.candidate',[4096,12288,8192,16384])
pr=Image.fromarray(core);pr.thumbnail((1400,1400));pr.save(out/'overview.preview-only.jpg',quality=94)
wr(out/'operations.json',ops);print(json.dumps({'repairs':len(items),'nativePixels':a.shape[0]*a.shape[1],'mismatches':0,'candidate':str(out/'r04_c02.candidate.png')}))
