from pathlib import Path
from PIL import Image,ImageFilter,ImageOps,ImageDraw
import numpy as np,json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[2]
Q=Path(__file__).resolve().parent
assert __import__('os').environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def arr(p):return np.asarray(Image.open(p).convert('RGB'))
def blue(a):
 a=a.astype(np.int16);return (a[:,:,2]>a[:,:,0]+25)&(a[:,:,2]>a[:,:,1]+15)&(a[:,:,2]>45)
def fill(a):
 im=ImageOps.expand(Image.fromarray(a.astype(np.uint8)*255),border=1,fill=0);ImageDraw.floodfill(im,(0,0),128);return np.asarray(im)[1:-1,1:-1]!=128
def silhouette(src,orig):
 m=fill(blue(src)|blue(orig));has=m.any(0);bottom=1253-m[::-1].argmax(0);m=(np.arange(1254)[:,None]<=bottom[None,:])&has[None,:]
 return m
bases=[R/'tiles/r09_c11.candidate-v02.png',R/'tiles/r09_c12.candidate-v06.png']
basearrays=[arr(p) for p in bases];outs=[a.copy() for a in basearrays];maps=[np.zeros((4096,4096),np.uint8) for _ in bases]
jobs=[]
for sid,letter,ox in [(1,'e',-397),(2,'f',627)]:
 f=R/f'native/r09_c12_roof_surface_{letter}_v01.png';src=arr(f);target=R/f'guides/r09_c12_roof_surface_{letter}_v01.target.png';orig=arr(target)
 mask=silhouette(src,orig)
 if letter=='f':
  # Measured native silhouette anchors replace the earlier rough root sketch.
  pts=np.array([(200,890),(210,920),(220,945),(235,976),(250,994),(275,1023),(300,1044),(340,1064),(400,1077),(450,1081),(480,1081),(520,1075),(550,1068),(575,1062),(600,1061),(625,1063),(650,1067),(690,1072),(750,1082),(800,1084)],float)
  xs=np.arange(200,801);rough=np.interp(xs,pts[:,0],pts[:,1]);trace=[]
  a=src.astype(float)
  for x,y in zip(xs,rough):
   lo=max(0,int(round(y))-7);hi=min(1250,int(round(y))+8)
   # Snap the ownership boundary to the downward dark contour near the measured silhouette.
   values=[float((a[k-2:k+1,max(0,x-1):x+2].mean((0,1))-a[k+1:k+4,max(0,x-1):x+2].mean((0,1))).mean()) for k in range(lo,hi)]
   trace.append(lo+int(np.argmax(values))+3)
  trace=np.asarray(trace)
  for x,y in zip(xs,trace):mask[:y+1,x]=True
  write(Q/'f01-gold-contour-proposal.json',{'native':str(f),'sourceSha256':sha(f),'xRange':[200,801],'bottomInclusive':trace.tolist(),'method':'Visual silhouette anchors with local native dark-edge snapping; ownership coordinates only, original RGB unchanged.','status':'proposal_requires_visual_review'})
 # A 2-pixel binary expansion includes the source anti-aliased object boundary, never RGB blending.
 mask=np.asarray(Image.fromarray(mask.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(5)))>0
 if letter=='e':mask[:,:115]=False;mask[:,1089:]=False
 else:mask[:,:65]=False;mask[:,1139:]=False
 mp=Q/f'{letter}-full-object-mask-v01.png';Image.fromarray(mask.astype(np.uint8)*255).save(mp)
 gx=np.arange(1254)+ox
 for i,tx in enumerate([-4096,0]):
  valid=(gx>=tx)&(gx<tx+4096);ix=np.where(valid)[0]
  if not len(ix):continue
  dx=gx[ix]-tx;m=mask[:,ix];reg=outs[i][742:1996,dx].copy();reg[m]=src[:,ix][m];outs[i][742:1996,dx]=reg
  ids=maps[i][742:1996,dx].copy();ids[m]=sid;maps[i][742:1996,dx]=ids
 jobs.append({'id':sid,'source':str(f),'sourceSha256':sha(f),'mask':str(mp),'maskSha256':sha(mp),'maskValues':[0,255],'originRelativeR09c12':[ox,742],'selectedPixels':int(mask.sum()),'worldCoordinatesUnchanged':True})
results=[]
for i,tid in enumerate(['r09_c11','r09_c12']):
 out=Q/f'{tid}-full-object-trial-v01.png';Image.fromarray(outs[i]).save(out)
 sm=Q/f'{tid}-source-id-v01.png';Image.fromarray(maps[i]).save(sm)
 replay=basearrays[i].copy()
 for j in jobs:
  ox,oy=j['originRelativeR09c12'];gx=np.arange(1254)+ox;tx=[-4096,0][i];valid=(gx>=tx)&(gx<tx+4096);ix=np.where(valid)[0]
  if not len(ix):continue
  dx=gx[ix]-tx;src=arr(j['source']);m=maps[i][oy:oy+1254,dx]==j['id'];reg=replay[oy:oy+1254,dx].copy();reg[m]=src[:,ix][m];replay[oy:oy+1254,dx]=reg
 assert np.array_equal(replay,outs[i])
 assert np.array_equal(outs[i][maps[i]==0],basearrays[i][maps[i]==0])
 assert np.array_equal(outs[i][1996:,:],basearrays[i][1996:,:])
 results.append({'file':str(out),'sha256':sha(out),'base':str(bases[i]),'baseSha256':sha(bases[i]),'sourceID':str(sm),'sourceIDSha256':sha(sm),'pixelReplayExact':True,'basePixelsOutsideMasksUnchanged':True,'allRowsFrom1996Unchanged':True})
 if tid=='r09_c12':
  Image.fromarray(outs[i]).resize((1024,1024),Image.Resampling.LANCZOS).save(Q/'full-object-preview-v01.png')
# All evidence below is unscaled exact trial pixel crops.
right=Image.fromarray(outs[1]);left=Image.fromarray(outs[0]);ev=[]
for name,box in [('ef',(540,1080,850,1800)),('fd',(1560,1120,1910,1880)),('roofwood-left',(0,1300,1024,1950)),('roofwood-scroll',(750,1350,1850,2100)),('bottom',(742,1800,1766,2180)),('top',(627,614,1881,870))]:
 p=Q/f'full-object-{name}-v01.png';right.crop(box).save(p);ev.append({'file':str(p),'sha256':sha(p),'r09c12Crop':box})
p=Q/'full-object-e-left-v01.png';left.crop((3686,742,3942,1390)).save(p);ev.append({'file':str(p),'sha256':sha(p),'r09c11Crop':[3686,742,3942,1390]})
write(Q/'proposal-v01.json',{'createdAt':datetime.now(timezone.utc).isoformat(),'author':'coordinate_audit','status':'trial_not_accepted_gold_internal_bar_remains','formalAccepted':False,'actualModel':None,'actualQuality':None,'outputs':results,'jobs':jobs,'sourceIdRule':'0 inherits base native pixels;1 E v01;2 F v01. No shift, RGB edits, alpha mixing, filtering or resampling in trial assets. Preview alone is reduced for overview.','efCutWorldX':692,'efTrueOverlapWorldX':[627,857],'fdCutWorldX':1766,'eLeftCutWorldX':-282,'evidence':ev,'knownBlocker':'Fv01 has an internal straight gold material line at its local x1024 / r09c12 x1651; complete-object mask cannot remove that preexisting native line. Root is producing complete-object G.'})
print(json.dumps({'folder':str(Q),'outputs':results,'efCut':692,'status':'trial_not_accepted_gold_internal_bar_remains'},indent=2))

