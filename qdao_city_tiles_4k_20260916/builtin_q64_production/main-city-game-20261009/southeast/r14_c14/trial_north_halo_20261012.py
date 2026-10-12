from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib,sys
from datetime import datetime,timezone
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;D=T/'repairs/north-halo-audit-20261012'
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def art(p):return {'path':str(p),'sha256':sha(p)}
def put(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2)
def png(p,a):
 with p.open('xb') as f:Image.fromarray(a).save(f,format='PNG')
proof=rd(D/'provenance.json');cur=rd(T/'candidate/latest-assembly.json')
for a in [proof['halo'],proof['selectedNeighbor'],proof['selectedNeighborContext'],cur['candidate'],cur['context']]:assert sha(a['path'])==a['sha256']
assert cur['candidate']['sha256']==proof['baseChild']['sha256']
base=np.array(Image.open(cur['candidate']['path']).convert('RGB'));ctx=np.array(Image.open(cur['context']['path']).convert('RGB'));north=np.array(Image.open(proof['selectedNeighbor']['path']).convert('RGB'));halo=np.array(Image.open(proof['halo']['path']).convert('RGB'))
# Independent per-pixel contributor replay, not just row concatenation.
z=np.load(proof['perPixelContributors']['path']);aa=z['first_source_index'];bb=z['second_source_index'];ww=z['second_source_weight'];yy,xx=np.mgrid[:115,:4096]
raws=[np.array(Image.open(a['native']['path']).convert('RGB')) for a in proof['nativeSources']]
ac=np.zeros_like(halo);bc=ac.copy()
for i,a in enumerate(raws):
 for ids,out in [(aa,ac),(bb,bc)]:
  match=ids==i;out[match]=a[(1139+yy)[match],(xx+115-1024*i)[match]]
assert np.array_equal(((ac.astype(np.uint32)*(255-ww[:,:,None])+bc.astype(np.uint32)*ww[:,:,None]+127)//255).astype(np.uint8),halo)
def path(cost):
 h,w=cost.shape;prev=cost[0].copy();back=np.zeros((h,w),np.int8)
 for y in range(1,h):
  vals=np.stack((np.pad(prev,(1,0),constant_values=1e30)[:w],prev,np.pad(prev,(0,1),constant_values=1e30)[1:]))
  ii=vals.argmin(0);back[y]=ii-1;prev=cost[y]+vals.min(0)
 p=np.empty(h,np.int32);p[-1]=prev.argmin()
 for y in range(h-1,0,-1):p[y-1]=p[y]+back[y,p[y]]
 return p
allout=[]
for mode in ['linear24','linear40','minerror8to96']:
 outdir=D/mode;outdir.mkdir()
 if mode.startswith('linear'):
  depth=int(mode[6:]);f=np.repeat(np.clip((depth-np.arange(115)[:,None])/depth,0,1),4096,axis=1);rule={'kind':'one-sided-linear','fullAtY':0,'zeroAtY':depth}
 else:
  a=halo[:,630:].astype(np.float32);b=base[:115,630:].astype(np.float32);cost=np.mean((a-b)**2,axis=2)*(1+40*((255-np.minimum(a.mean(2),b.mean(2)))/255)**3)
  seam=path(cost[8:97].T)+8;np.save(outdir/'minimum-error-path.npy',seam);full=np.zeros(4096,np.int32);full[630:]=seam
  f=np.clip((full[None,:]-np.arange(115)[:,None]+2)/4,0,1);rule={'kind':'one-sided-minimum-error','searchY':[8,96],'featherTotalPixels':4,'path':art(outdir/'minimum-error-path.npy'),'pathMin':int(seam.min()),'pathMax':int(seam.max()),'cost':'mean RGB squared difference*(1+40*((255-min(meanSource,meanBase))/255)^3)'}
 f*=np.clip((np.arange(4096)-630)/32,0,1)[None,:]
 alpha=np.rint(f*255).astype(np.uint8);assert not alpha[:,:630].any()
 png(outdir/'alpha.png',alpha);a=alpha[:,:,None].astype(np.uint32);out=base.copy();out[:115]=((halo.astype(np.uint32)*a+base[:115].astype(np.uint32)*(255-a)+127)//255).astype(np.uint8)
 assert np.array_equal(out[:630,:630],base[:630,:630]);assert np.array_equal(out[115:],base[115:]);assert np.array_equal(out[:115][alpha==0],base[:115][alpha==0])
 cp=T/'candidate'/('r14_c14-4k-north-halo-'+mode+'-trial-20261012.png');png(cp,out)
 cx=ctx.copy();cx[115:4211,115:4211]=out;ctp=T/'candidate'/('r14_c14-context-north-halo-'+mode+'-trial-20261012.png');png(ctp,cx)
 views=[]
 for x in [630,1600,2842]:
  im=np.concatenate((north[3456:4096,x:x+1254],out[:614,x:x+1254]));p=outdir/f'joined-x{x}-1254.png';png(p,im);views.append(art(p))
  p=outdir/f'seam-x{x}-100pct.png';png(p,im[600:820]);views.append(art(p))
 for x in [630,1024,2048,3072]:
  x0=max(0,x-180);x1=min(4096,x+180);im=np.concatenate((north[3896:,x0:x1],out[:200,x0:x1]));p=outdir/f'join-endpoint-x{x}-100pct.png';png(p,im);views.append(art(p))
 record={'createdAt':datetime.now(timezone.utc).isoformat(),'status':'trial_pending_visual_qa','baseCandidate':cur['candidate'],'baseContext':cur['context'],'nativeProvenance':art(D/'provenance.json'),'sourceHalo':proof['halo'],'nativeSourceCropInNeighborContext':[115,4211,4211,4326],'targetBox':[0,0,4096,115],'alpha':art(outdir/'alpha.png'),'alphaRule':rule,'leftProtectionFadeX':[630,662],'compositor':art(Path(__file__)),'operation':'native integer crop and saved alpha; uint32 (native*a+base*(255-a)+127)//255; no RGB correction or resize','candidate':art(cp),'context':art(ctp),'views':views,'pixelContributorReplay':True,'frozen630Unchanged':True,'outsideAlphaUnchanged':True,'northCoreUnchanged':True,'newGenerationCount':0,'formalAccepted':False}
 put(outdir/'composition.json',record);allout.append({'mode':mode,'candidate':record['candidate'],'manifest':art(outdir/'composition.json'),'alphaRule':rule})
put(D/'trial-index.json',{'trials':allout,'allUnpublished':True,'currentCandidate':cur['candidate'],'imagegenCalled':False});print(json.dumps(allout,indent=2))

