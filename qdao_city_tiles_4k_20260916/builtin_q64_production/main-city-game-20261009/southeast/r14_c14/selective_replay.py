from pathlib import Path
import json,sys,hashlib,importlib.util
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;R=T/'repairs'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
 if not v:raise ValueError(m)
def art(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}
def check(d):need(sha(d['path'])==d['sha256'],'Changed '+d['path'])
def write(p,d):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(d,f,indent=2)
def png(p,d):
 with Path(p).open('xb') as f:d.save(f,format='PNG')
def apply(native_version,label,boxes):
 d=R/native_version;p=read(d/'preparation.json');g=read(d/'generation.json');boxes=json.loads(boxes)
 cur=read(R/'latest-repair.json') if (R/'latest-repair.json').exists() else read(T/'candidate/latest-assembly.json')
 for k in ['candidate','context']:check(cur[k])
 for a in [g['native'],g['originalOutput'],g['receipt'],g['preparation'],p['rawTarget'],p['sourceCandidate'],p['request'],p['prompt']]+p['references']:check(a)
 out=R/label;out.mkdir(exist_ok=False)
 base=np.array(Image.open(cur['candidate']['path']).convert('RGB'));raw=np.array(Image.open(p['rawTarget']['path']).convert('RGB'));gen=np.array(Image.open(g['native']['path']).convert('RGB'));need(gen.shape==(1254,1254,3),'Native size')
 x,y,x1,y1=p['sourceCropIn4096'];old=base[y:y1,x:x1].copy();alpha=np.zeros((1254,1254),np.uint8)
 for a,b,c,e in boxes:
  need(0<=a<c<=1254 and 0<=b<e<=1254,'Box')
  yy,xx=np.mgrid[b:e,a:c];dist=np.minimum.reduce([xx-a,yy-b,c-1-xx,e-1-yy])
  alpha[b:e,a:c]=np.maximum(alpha[b:e,a:c],np.uint8(np.clip(dist/2,0,1)*255))
 need(np.array_equal(old[alpha>0],raw[alpha>0]),'Changed applied region')
 aa=alpha[:,:,None].astype(np.uint32);base[y:y1,x:x1]=((old.astype(np.uint32)*(255-aa)+gen.astype(np.uint32)*aa+127)//255).astype(np.uint8)
 png(out/'alpha.png',Image.fromarray(alpha))
 candidate=T/'candidate'/('r14_c14-4k-'+label+'.png');png(candidate,Image.fromarray(base))
 ctx=np.array(Image.open(cur['context']['path']).convert('RGB'));ctx[115:4211,115:4211]=base
 context=T/'candidate'/('r14_c14-context-'+label+'.png');png(context,Image.fromarray(ctx))
 png(out/'review-1254.png',Image.fromarray(base[y:y1,x:x1]))
 m={'version':label,'tile':'r14_c14','sourceCandidate':cur['candidate'],'sourceContext':cur['context'],'candidate':art(candidate),'context':art(context),'native':g['native'],'generation':art(d/'generation.json'),'preparation':art(d/'preparation.json'),'receipt':g['receipt'],'originalOutput':g['originalOutput'],'placement':p['sourceCropIn4096'],'alpha':art(out/'alpha.png'),'rectanglesInNative':boxes,'compositor':art(Path(__file__)),'rule':'Unscaled selected actual-native rectangle union; outer2px linear alpha; all other pixels unchanged. Pixel arithmetic uint32 rounded. Original guide boxes do not restrict downstream native selection; selections are explicitly recorded here.','formalAccepted':False}
 write(out/'composition.json',m);replay(str(out/'composition.json'));return m
def replay(manifest):
 m=read(manifest)
 for k in ['sourceCandidate','sourceContext','candidate','context','native','generation','preparation','receipt','originalOutput','alpha','compositor']:check(m[k])
 g=read(m['generation']['path']);p=read(m['preparation']['path'])
 for a in p['references']+[p['request'],p['prompt'],p['rawTarget'],p['sourceCandidate']]:check(a)
 need(g['originalOutput']['sha256']==g['native']['sha256'],'Native bytes')
 x,y,x1,y1=m['placement'];raw=Image.open(p['sourceCandidate']['path']).convert('RGB').crop((x,y,x1,y1))
 need(np.array_equal(np.array(raw),np.array(Image.open(p['rawTarget']['path']).convert('RGB'))),'Raw replay')
 src=np.array(Image.open(m['sourceCandidate']['path']).convert('RGB'));result=src.copy();a=np.array(Image.open(m['alpha']['path']))[:,:,None].astype(np.uint32);gen=np.array(Image.open(m['native']['path']).convert('RGB'))
 result[y:y1,x:x1]=((src[y:y1,x:x1].astype(np.uint32)*(255-a)+gen.astype(np.uint32)*a+127)//255).astype(np.uint8)
 need(np.array_equal(result,np.array(Image.open(m['candidate']['path']).convert('RGB'))),'Candidate replay')
 ctx=np.array(Image.open(m['sourceContext']['path']).convert('RGB'));ctx[115:4211,115:4211]=result
 need(np.array_equal(ctx,np.array(Image.open(m['context']['path']).convert('RGB'))),'Context replay')
 initial=read(T/'candidate/latest-assembly.json')
 if 'initialAssembly' in initial:initial=initial['initialAssembly']
 # Root reserves original northwest [0,0,630,630].
 original=np.array(Image.open(T/'candidate/r14_c14-4k-candidate-8ff54f4e9ec7de483b1a.png').convert('RGB'))
 need(np.array_equal(result[:630,:630],original[:630,:630]),'Root reserved corner changed')
 return {'replayed':True,'reservedCornerUnchanged':True,'candidateSha256':sha(m['candidate']['path'])}
if __name__=='__main__':print(json.dumps(globals()[sys.argv[1]](*sys.argv[2:]),indent=2))

