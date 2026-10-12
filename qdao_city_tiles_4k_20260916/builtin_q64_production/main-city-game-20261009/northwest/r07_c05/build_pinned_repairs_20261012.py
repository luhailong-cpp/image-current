from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;Z=T.parent;sys.path.insert(0,str(Z))
import production_v2 as p
import assemble_native as A
def ref(f):return {'file':str(f),'sha256':p.sha(f)}
D=T/'qa/pinned-repairs-trial-01';D.mkdir(exist_ok=True);assert not (D/'index.json').exists()
bp=T/'qa/partial-curb-trial-01/index.json';m=p.read(bp);pix=np.array(Image.open(m['candidate']['file']).convert('RGB'));own=np.array(Image.open(m['sourceIndex']['file']));sources=m['sources'];operations=[]
for bid in ['curb-junction-02','curb-junction-03']:
 g=p.read(T/'bridges'/bid/'generation.json');pl=p.read(T/'bridges'/bid/'placement.json');sources.append({'id':bid,'file':g['file'],'sha256':g['sha256'],'tileOriginXY':pl['tileBox'][:2],'generationRecord':ref(T/'bridges'/bid/'generation.json')})
specs=[('upper-curb-blue','curb-junction-02',[430,120,900,610],[80,80,60,50]),('lower-curb','curb-junction-03',[450,560,1040,850],[100,100,40,60]),('floor','curb-junction-02',[460,790,880,1254],[90,90,45,65])]
for name,bid,box,bands in specs:
 sid=next(i for i,s in enumerate(sources) if s['id']==bid);s=sources[sid];bx,by,bx2,by2=box;w=bx2-bx;h=by2-by;x=s['tileOriginXY'][0]+bx;y=s['tileOriginXY'][1]+by
 new=np.array(Image.open(s['file']).convert('RGB'))[by:by2,bx:bx2];old=pix[y:y+h,x:x+w].copy();wl,wr,wt,wb=bands
 left=A.minimum_vertical_seam(old[:,:wl],new[:,:wl]);right=A.minimum_vertical_seam(new[:,-wr:],old[:,-wr:])+w-wr;top=A.minimum_vertical_seam(old[:wt].transpose(1,0,2),new[:wt].transpose(1,0,2));bottom=A.minimum_vertical_seam(new[-wb:].transpose(1,0,2),old[-wb:].transpose(1,0,2))+h-wb
 yy,xx=np.indices((h,w));mask=(xx>=left[:,None])&(xx<right[:,None])&(yy>=top[None,:])&(yy<bottom[None,:]);mask[[0,-1]]=False;mask[:,[0,-1]]=False
 pix[y:y+h,x:x+w][mask]=new[mask];own[y:y+h,x:x+w][mask]=sid;operations.append({'name':name,'sourceIndex':sid,'sourceCropLTRB':box,'tileBox':[x,y,x+w,y+h],'maskPaths':{'left':left.tolist(),'right':right.tolist(),'top':top.tolist(),'bottom':bottom.tolist()},'selectedPixels':int(mask.sum())})
proof=[]
for i,s in enumerate(sources):
 ys,xs=np.where(own==i);n=np.array(Image.open(s['file']).convert('RGB'));ox,oy=s['tileOriginXY'];assert p.sha(s['file'])==s['sha256'];assert np.array_equal(pix[ys,xs],n[ys-oy,xs-ox]);proof.append({'sourceIndex':i,'pixelCount':int(len(xs)),'exactNativePixels':True})
im=Image.fromarray(pix);out=A.save_png(im,D/'candidate.png');oi=A.save_png(Image.fromarray(own),D/'source-index.png');qa=A.write_qa(im,out,D/'internal');entries=[]
for o in operations:
 x,y,x2,y2=o['tileBox'];box=[max(0,x-130),max(0,y-130),min(4096,x2+130),min(4096,y2+130)];e=A.save_png(im.crop(box),D/(o['name']+'-region.png'));e.update(name=o['name'],cropLTRB=box,nativePixelScale=1,actuallyViewed=False);entries.append(e)
p.write_json(D/'index.json',{'candidate':out,'sourceIndex':oi,'sources':sources,'pixelProof':proof,'fullNativePixelProof':True,'resampled':False,'blended':False,'priorTrial':ref(bp),'operations':operations,'internalQa':qa,'entries':entries,'formalAccepted':False},replace=False);print(out)
