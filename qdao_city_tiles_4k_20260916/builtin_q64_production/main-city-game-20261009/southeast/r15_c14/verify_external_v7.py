from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;Z=T.parent;R=T/'review/external-partial-v7-20261013';R.mkdir(exist_ok=True)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def rec(p):return {'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def checked(r):assert rec(r['path'])['sha256']==r['sha256'];return Path(r['path'])
chain=[]
def collect(p):
 m=read(p)
 if m.get('previousComposition'):collect(checked(m['previousComposition']))
 chain.append((p,m))
collect(T/'repairs/edge-continuity-v7-20261012/composition.json')
previous=None;results=[];count=0;natives=set()
for mp,m in chain:
 base=checked(m['base']);a=np.asarray(Image.open(base).convert('RGB')).copy()
 if previous is not None:assert np.array_equal(a,previous)
 for s in m['steps']:
  n=checked(s['native']);natives.add(str(n));assert Image.open(n).size==(1254,1254);checked(s['receipt']);ap=checked(s['alpha']);x0,y0,x1,y1=s['placement'];new=np.asarray(Image.open(n).convert('RGB').crop(s['sourceCrop']),dtype='uint32');alpha=np.asarray(Image.open(ap),dtype='uint32')[:,:,None];old=a[y0:y1,x0:x1].astype('uint32');a[y0:y1,x0:x1]=((new*alpha+old*(255-alpha)+127)//255).astype('uint8');count+=1
 assert np.array_equal(a,np.asarray(Image.open(checked(m['candidate'])).convert('RGB')))
 context=Image.open(checked(m['baseContext'])).convert('RGB');context.paste(Image.fromarray(a),(115,115));assert np.array_equal(np.asarray(context),np.asarray(Image.open(checked(m['context'])).convert('RGB')))
 previous=a;results.append({'composition':rec(mp),'candidate':m['candidate'],'exactPixelReplay':True,'contextExactPixelReplay':True})
current=chain[-1][1];im=Image.fromarray(previous);images=[];sources={}
initial=np.asarray(Image.open(T/'candidate/r15_c14-4k-candidate-c7fe4d0fb7016f67422f.png').convert('RGB'));assert np.array_equal(initial[-115:],previous[-115:])
for edge,tile in [('north','r14_c14'),('west','r15_c13')]:
 src=read(Z/tile/'candidate/latest-assembly.json');sources[edge]=src;neighbor=Image.open(checked(src['candidate'])).convert('RGB')
 for k in range(4):
  start=k*1024
  if edge=='north':
   out=Image.new('RGB',(1024,800));out.paste(neighbor.crop((start,3696,start+1024,4096)),(0,0));out.paste(im.crop((start,0,start+1024,400)),(0,400))
  else:
   out=Image.new('RGB',(800,1024));out.paste(neighbor.crop((3696,start,4096,start+1024)),(0,0));out.paste(im.crop((0,start,400,start+1024)),(400,0))
  p=R/f'{edge}-joint-{k+1}-100pct.png';out.save(p);images.append({'edge':edge,'segment':k+1,'tileRange':[start,start+1024],'image':rec(p),'native100pct':True})
out={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate':current['candidate'],'context':current['context'],'selectedCompositionChain':results,'replayedAlphaSteps':count,'nativeSourcesUsed':len(natives),'sourceNativeDimensions':[1254,1254],'sourceResize':False,'rgbColorCorrection':False,'southLast115Unchanged':True,'neighborSourceSelections':sources,'reviewImages':images,'formalAccepted':False}
(R/'replay-validation.json').write_text(json.dumps(out,indent=2));print(json.dumps({'steps':count,'nativeSources':len(natives),'report':rec(R/'replay-validation.json')}))

