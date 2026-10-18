from pathlib import Path
import json,hashlib,sys,shutil,importlib.util
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageFilter
T=Path(__file__).resolve().parent;Z=T.parent
D=T/'repairs/roof-local-details-20261013-v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'path':str(p),'sha256':sha(p)}
def write(p,v):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def png(p,im):
 with Path(p).open('xb') as f:im.save(f,format='PNG')
def prepare():
 D.mkdir(parents=True,exist_ok=True);L=read(T/'candidate/latest-assembly.json')
 assert L['candidate']['sha256']=='d82e10271efc8fea51d7c5e60470a449078a44dae7cf4617c5c60b0c72de73fc'
 assert sha(L['candidate']['path'])==L['candidate']['sha256']
 C=Image.open(L['candidate']['path']).convert('RGB')
 jobs=[('A-corner-curl',[2842,2842,4096,4096],[3200,3400,3660,4040], 'Remove ONLY the large protruding spiral scroll ornament near local x 560 y 875. Continue the existing plain gold roof edge in a smooth simple bend through this location, with the same width and shading as the adjoining gold edge. Restore any uncovered red structural wood and blue roof tiles naturally. Keep the main plain curved roof edge, tiles, circular blue eave caps, red column, stone wall and all other geometry exactly. Do not replace the spiral with another ornament, medallion, clasp or knot. The plain bend should follow the existing gold edge through this corner, without a hanging curled tip.'),
 ('B-right-shrub',[2842,1850,4096,3104],[3750,2160,4096,2610], 'Remove ONLY the small unauthorized leafy shrub at local far right around x 1170 y 545. Reconstruct the existing pale grey stone parapet/wall and its natural shadow behind it, continuing the visible straight wall edges and grout. Keep all blue roof tiles, curved gold roof edge, pond water and every other object exactly. No new vegetation, pots, ornament or architecture. The wall continues past the right crop edge.'),
 ('C-rib-connection',[1550,1450,2804,2704],[2000,1770,2510,2390], 'Fix ONLY the broken gold diagonal roof rib: the thin rib currently ends abruptly over blue roof tiles near local x 635 y 790. Extend this same thin gold rib upward/right along its existing straight direction until it naturally joins the underside of the existing upper gold ridge at about local x 790 y 350. The rib must be a continuous structural gold strip between the existing middle band below and the upper ridge above, with consistent width and matching light/shadow. Keep all other ridge shapes, existing roof tiles, finial, water, leaf and the original framing exactly. Do not add a new separate bar, clasp, ornament, extra tiers or other roof edges.')]
 for key,crop,box,detail in jobs:
  J=D/key;J.mkdir(exist_ok=True);target=J/'edit-target-native-1254.png';png(target,C.crop(crop))
  prompt='Use case: precise-object-edit. Edit the attached native 1254 x 1254 crop of the approved Taoist chibi game map. Output the same 1254 x 1254 opaque native crop with identical framing, perspective and scale. This is a small detail crop, never reframe to show a complete building. '+detail+' Preserve the clean hand-painted native detail and existing natural daylight. Change only the named local defect; all surrounding pixels should remain stable. No blur, repaint of the whole scene, labels, text, grid or watermark.'
  req={'prompt':prompt,'referenced_image_paths':[str(target)],'transparent_background':False}
  write(J/'request.json',req);(J/'prompt.txt').write_text(prompt,encoding='utf-8')
  write(J/'preparation.json',{'tile':T.name,'id':key,'sourceCandidate':L['candidate'],'sourceContext':L['context'],'sourceAssembly':L['manifest'],'target':info(target),'cropBox':crop,'pasteBox':box,'request':info(J/'request.json'),'actualModel':None,'actualQuality':None,'formalAccepted':False})
 print(json.dumps({'directory':str(D),'jobs':[j[0] for j in jobs]}))
def save(key,original):
 J=D/key;m=read(J/'preparation.json');original=Path(original);native=J/'repair-native-1254.png'
 im=Image.open(original);assert im.size==(1254,1254) and im.format=='PNG'
 if im.mode=='RGBA':assert im.getextrema()[3]==(255,255)
 assert not native.exists();shutil.copyfile(original,native);assert sha(native)==sha(original)
 rec={'tool':'image_gen.imagegen','route':'builtin','status':'succeeded_pending_visual_review','actualModel':None,'actualQuality':None,'savedAtUtc':datetime.now(timezone.utc).isoformat(),'generatedAtUtc':None,'original':info(original),'native':info(native),'request':info(J/'request.json'),'preparation':info(J/'preparation.json'),'resized':False,'formalAccepted':False}
 write(J/'receipt.json',rec);write(J/'repair-native-1254.png.generation.json',dict(rec,tile=T.name,width=1254,height=1254,file=str(native),sha256=sha(native)))
 print(json.dumps(rec))
def compose(keys):
 m0=read(D/keys[0]/'preparation.json');base=np.array(Image.open(m0['sourceCandidate']['path']).convert('RGB'));result=base.copy();steps=[]
 spec=importlib.util.spec_from_file_location('alg',Z/'assemble_candidate.py');alg=importlib.util.module_from_spec(spec);spec.loader.exec_module(alg)
 O=D/('composed-'+'-'.join(k[0] for k in keys));O.mkdir(exist_ok=False)
 for key in keys:
  J=D/key;m=read(J/'preparation.json');assert m['sourceCandidate']==m0['sourceCandidate'];assert sha(m['target']['path'])==m['target']['sha256']
  box=([1830,1620,2380,2704] if key=='C-rib-connection' else [2180,1610,2804,2704] if key=='D-right-rib-connection' else m['pasteBox']);crop=m['cropBox'];sx,sy=box[0]-crop[0],box[1]-crop[1];h,w=box[3]-box[1],box[2]-box[0]
  old=result[box[1]:box[3],box[0]:box[2]].copy();new=np.array(Image.open(J/'repair-native-1254.png').convert('RGB'))[sy:sy+h,sx:sx+w]
  b=40;paths={'left':alg.minimum_vertical_seam(old[:,:b],new[:,:b]),'right':alg.minimum_vertical_seam(old[:,-b:],new[:,-b:]),'top':alg.minimum_vertical_seam(old[:b].transpose(1,0,2),new[:b].transpose(1,0,2)),'bottom':alg.minimum_vertical_seam(old[-b:].transpose(1,0,2),new[-b:].transpose(1,0,2))}
  a=np.full((h,w),255,np.uint8)
  a[:,:b]=np.where(np.arange(b)[None,:]>=paths['left'][:,None],255,0)
  if box[2]<4096:a[:,-b:]=np.minimum(a[:,-b:],np.where(np.arange(b)[None,:]<paths['right'][:,None],255,0).astype(np.uint8))
  a[:b]=np.minimum(a[:b],np.where(np.arange(b)[:,None]>=paths['top'][None,:],255,0).astype(np.uint8))
  a[-b:]=np.minimum(a[-b:],np.where(np.arange(b)[:,None]<paths['bottom'][None,:],255,0).astype(np.uint8))
  a=np.array(Image.fromarray(a).filter(ImageFilter.GaussianBlur(2)));a[0]=0;a[-1]=0;a[:,0]=0
  if box[2]<4096:a[:,-1]=0
  ap=O/(key+'-alpha.png');png(ap,Image.fromarray(a));sp=O/(key+'-seams.npz')
  with sp.open('xb') as f:np.savez_compressed(f,**paths)
  mixed=((old.astype(np.uint32)*(255-a[:,:,None])+new.astype(np.uint32)*a[:,:,None]+127)//255).astype(np.uint8)
  result[box[1]:box[3],box[0]:box[2]]=mixed
  png(O/(key+'-local-100pct.png'),Image.fromarray(result).crop(crop))
  steps.append({'id':key,'native':info(J/'repair-native-1254.png'),'receipt':info(J/'receipt.json'),'preparation':info(J/'preparation.json'),'nativeCrop':[sx,sy,sx+w,sy+h],'pasteBox':box,'preparedPasteBox':m['pasteBox'],'adoptionAdjustment':('After native inspection include full connected rib up to the existing ridge and down to the existing lower gold band; no source resizing.' if key=='C-rib-connection' else None),'alpha':info(ap),'seams':info(sp)})
 png(O/'candidate-4096.png',Image.fromarray(result));ctx=np.array(Image.open(m0['sourceContext']['path']).convert('RGB'));ctx[115:4211,115:4211]=result;png(O/'context-4326.png',Image.fromarray(ctx))
 # Replay using stored alpha independently from seam construction.
 replay=Image.open(m0['sourceCandidate']['path']).convert('RGB');rp=replay.load()
 for s in steps:
  x,y,x1,y1=s['pasteBox'];sx,sy,_,_=s['nativeCrop'];npix=Image.open(s['native']['path']).convert('RGB').load();aim=Image.open(s['alpha']['path']).convert('L');apix=aim.load()
  for yy in range(y1-y):
   for xx in range(x1-x):
    av=apix[xx,yy]
    if av:
     oo=rp[x+xx,y+yy];nn=npix[sx+xx,sy+yy];rp[x+xx,y+yy]=tuple((oo[c]*(255-av)+nn[c]*av+127)//255 for c in range(3))
 assert np.array_equal(np.array(replay),result)
 support=np.zeros((4096,4096),bool)
 for s in steps:
  x,y,x1,y1=s['pasteBox'];support[y:y1,x:x1]|=np.array(Image.open(s['alpha']['path']))>0
 changed=np.any(result!=base,axis=2);assert not changed[~support].any();ys,xs=np.where(changed)
 png(O/'overview-preview-only.png',Image.fromarray(result).resize((1024,1024),Image.Resampling.LANCZOS))
 out={'sourceCandidate':m0['sourceCandidate'],'sourceContext':m0['sourceContext'],'sourceAssembly':m0['sourceAssembly'],'steps':steps,'candidate':info(O/'candidate-4096.png'),'context':info(O/'context-4326.png'),'scalarReplayExact':True,'outsideSavedAlphaUnchanged':True,'contextCoreExact':True,'resizedArt':False,'rgbColorCorrection':False,'alphaBlurRadius':2,'actualChangeBox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'compositor':info(__file__),'status':'unpublished_pending_visual_review','formalAccepted':False}
 write(O/'composition.json',out);print(json.dumps(out))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 elif sys.argv[1]=='save':save(sys.argv[2],sys.argv[3])
 elif sys.argv[1]=='compose':compose(sys.argv[2:])
