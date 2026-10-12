"""Tile-only native bridge audit and assembly. No painting, resizing or blending."""
from pathlib import Path
import sys,json,hashlib,shutil,argparse,importlib.util,datetime
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('native_assembler',P.parent/'assemble_native.py')
A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 data=(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
 if p.exists():
  if p.read_bytes()==data:return
  raise FileExistsError(p)
 p.write_bytes(data)
def ref(p): return dict(file=str(Path(p).resolve()),sha256=sha(p))
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def bridge_dir(i):
 if not i.replace('-','').replace('_','').isalnum():raise ValueError(i)
 return P/'bridges'/i
def prepare(args):
 m=read(args.manifest);p=Path(m['output']['file'])
 assert sha(p)==m['output']['sha256']
 x,y=args.xy;assert 0<=x<=2842 and 0<=y<=2842
 d=bridge_dir(args.id);d.mkdir(parents=True,exist_ok=True)
 out=d/'edit-target.png';im=Image.open(p).convert('RGB').crop((x,y,x+1254,y+1254))
 if out.exists():assert Image.open(out).tobytes()==im.tobytes()
 else:im.save(out)
 write(d/'placement.json',dict(schemaVersion=1,id=args.id,createdAtUtc=now(),kind='additional-native-seam-bridge-not-fixed-grid-source',tile='r07_c04',tileBox=[x,y,x+1254,y+1254],worldBox=[12288+x,24576+y,12288+x+1254,24576+y+1254],nativePixels=[1254,1254],nativePixelScale=1,sourceResampled=False,editTarget=ref(out),derivedFrom=ref(p),baseManifest=ref(args.manifest)))
 print(out)
def request(args):
 d=bridge_dir(args.id);pl=read(d/'placement.json');a=read(args.parameters)
 refs=[ref(p) for p in a['referenced_image_paths']]
 write(d/'request.json',dict(schemaVersion=1,requestedAtUtc=now(),route='builtin_image_gen',exactParameters=a,placement=ref(d/'placement.json'),references=refs,actualModel=None,actualQuality=None,successNotImplied=True))
 (d/'prompt.txt').write_text(a['prompt'],encoding='utf-8')
 print('recorded')
def ingest(args):
 d=bridge_dir(args.id);pl=read(d/'placement.json');req=read(d/'request.json');src=Path(args.source);receipt=read(args.receipt)
 with Image.open(src) as im:
  assert im.format=='PNG' and im.size==(1254,1254) and im.convert('RGBA').getchannel('A').getextrema()==(255,255)
 out=d/'native.png'
 if out.exists():assert sha(out)==sha(src)
 else:shutil.copyfile(src,out)
 write(d/'generation.json',dict(schemaVersion=1,id=args.id,generatedAtUtc=now(),kind=pl['kind'],route='builtin_image_gen',sourceHostFile=str(src),sourceHostSha256=sha(src),file=str(out),sha256=sha(out),width=1254,height=1254,worldBox=pl['worldBox'],tileBox=pl['tileBox'],resizedAfterGeneration=False,finalArtUpscaled=False,request=ref(d/'request.json'),toolReceipt=ref(args.receipt),actualModel=None,actualQuality=None))
 print(json.dumps(ref(out)))
def rebuild_owners(m):
 paths=m['seamPaths'];rows=[]
 for r in range(1,5):
  strip=np.full((1254,1254),(r-1)*4,dtype=np.uint8)
  for c in range(2,5):
   path=np.array(next(p['overlapPath'] for p in paths if p['axis']=='x' and p['patchRow']==r and p['nextPatchColumn']==c))
   mask=np.arange(230)[None,:]>=path[:,None]
   joined=np.where(mask,(r-1)*4+c-1,strip[:,-230:]).astype(np.uint8)
   strip=np.concatenate([strip[:,:-230],joined,np.full((1254,1024),(r-1)*4+c-1,np.uint8)],axis=1)
  rows.append(strip)
 strip=rows[0].T
 for r in range(2,5):
  path=np.array(next(p['overlapPath'] for p in paths if p['axis']=='y' and p['nextPatchRow']==r))
  mask=np.arange(230)[None,:]>=path[:,None]
  right=rows[r-1].T
  strip=np.concatenate([strip[:,:-230],np.where(mask,right[:,:230],strip[:,-230:]),right[:,230:]],axis=1)
 return strip.T[115:4211,115:4211].copy()
def verify(pixels,owners,sources):
 assert owners.shape==(4096,4096) and pixels.shape==(4096,4096,3)
 checked=0;counts={}
 for i,s in enumerate(sources):
  assert sha(s['file'])==s['sha256']
  a=np.asarray(Image.open(s['file']).convert('RGB'));assert a.shape==(1254,1254,3)
  ys,xs=np.where(owners==i);ox,oy=s['tileOriginXY']
  if len(xs):
   assert (xs>=ox).all() and (ys>=oy).all() and (xs<ox+1254).all() and (ys<oy+1254).all()
   assert np.array_equal(pixels[ys,xs],a[ys-oy,xs-ox]),s['file']
  counts[str(i)]=len(xs);checked+=len(xs)
 assert checked==4096*4096
 return dict(status='passed',checkedPixels=checked,allPixelsUnmodifiedNativeSamplesAtExactWorldCoordinates=True,countsBySource=counts)
def assemble(args):
 cfg=read(args.config);m=read(cfg['baseManifest']);assert sha(m['output']['file'])==m['output']['sha256']
 pixels=np.asarray(Image.open(m['output']['file']).convert('RGB')).copy();owners=rebuild_owners(m)
 sources=[]
 for s in m['nativeSources']:
  sources.append(dict(**s,tileOriginXY=[(s['column']-1)*1024-115,(s['row']-1)*1024-115]))
 initial=verify(pixels,owners,sources);bridges=[]
 for item in cfg['bridges']:
  d=bridge_dir(item['id']);g=read(d/'generation.json');pl=read(d/'placement.json')
  assert sha(g['file'])==g['sha256'];x,y,x2,y2=pl['tileBox']
  b=np.asarray(Image.open(g['file']).convert('RGB'));old=pixels[y:y2,x:x2].copy();w=item.get('border',230)
  assert 32<=w<=400
  l=A.minimum_vertical_seam(old[:,:w],b[:,:w])
  r=A.minimum_vertical_seam(b[:,-w:],old[:,-w:])+1254-w
  top=A.minimum_vertical_seam(old[:w].transpose(1,0,2),b[:w].transpose(1,0,2))
  bot=A.minimum_vertical_seam(b[-w:].transpose(1,0,2),old[-w:].transpose(1,0,2))+1254-w
  yy,xx=np.indices((1254,1254));mask=(xx>=l[:,None])&(xx<r[:,None])&(yy>=top[None,:])&(yy<bot[None,:])
  # Keep an exact unchanged outermost perimeter even in edge-hugging cut cases.
  mask[[0,-1],:]=False;mask[:,[0,-1]]=False
  pixels[y:y2,x:x2][mask]=b[mask];owners[y:y2,x:x2][mask]=len(sources)
  sources.append(dict(id=item['id'],file=g['file'],sha256=g['sha256'],nativePixels=[1254,1254],tileOriginXY=[x,y],worldBox=pl['worldBox'],kind=pl['kind'],generationRecord=ref(d/'generation.json'),request=ref(d/'request.json'),receipt=g['toolReceipt'],sourceHostFile=g['sourceHostFile'],sourceHostSha256=g['sourceHostSha256'],sourceResampled=False))
  bridges.append(dict(id=item['id'],tileBox=pl['tileBox'],worldBox=pl['worldBox'],nativePixels=[1254,1254],changedPixels=int(mask.sum()),border=w,paths=dict(left=l.tolist(),right=r.tolist(),top=top.tolist(),bottom=bot.tolist())))
 proof=verify(pixels,owners,sources)
 script=ref(__file__);signature=hashlib.sha256(json.dumps(dict(config=cfg,sources=sources,script=script),sort_keys=True).encode()).hexdigest()[:16]
 name='r07_c04-candidate-native-bridges-'+signature;od=P/'candidate'/name;assert not od.exists();od.mkdir()
 out=A.save_png(Image.fromarray(pixels),od/'candidate.png')
 owner=A.save_png(Image.fromarray(owners),od/'source-index.png')
 assert np.array_equal(np.asarray(Image.open(owner['file'])),owners)
 qa=A.write_qa(Image.fromarray(pixels),out,P/'qa'/name)
 bqa=[]
 for b in bridges:
  x,y,x2,y2=b['tileBox']
  for side,box,rot in [('top',[x,max(0,y-80),x2,min(4096,y+320)],False),('bottom',[x,max(0,y2-320),x2,min(4096,y2+80)],False),('left',[max(0,x-80),y,min(4096,x+320),y2],True),('right',[max(0,x2-320),y,min(4096,x2+80),y2],True)]:
   im=Image.fromarray(pixels).crop(box)
   if rot:im=im.transpose(Image.Transpose.ROTATE_90)
   q=A.save_png(im,P/'qa'/name/(b['id']+'-boundary-'+side+'.png'));q.update(cropLTRB=box,rotationCCW90=rot,sourceResampled=False,nativePixelScale=1,derivedFrom=out)
   bqa.append(q)
 result=dict(schemaVersion=2,createdAtUtc=now(),tile='r07_c04',status='candidate_pending_visual_review',output=out,baseManifest=ref(cfg['baseManifest']),fixedGridSourceCount=16,additionalNativeBridgeCount=len(bridges),totalNativeSourceCount=len(sources),nativeSources=sources,bridges=bridges,sourceIndex=owner,sourceIndexEncoding='uint8; value is 0-based nativeSources index; coordinates calculated from tileOriginXY',pixelProof=proof,basePixelProof=initial,sourceResampled=False,feathering=False,blending=False,script=script,dependency=ref(A.__file__),config=ref(args.config),qa=qa,bridgeBoundaryQa=bqa,formalAccepted=False)
 write(od/'assembly.json',result);print(json.dumps(dict(output=out,manifest=str(od/'assembly.json'),qaDirectory=str(P/'qa'/name),pixelProof=proof),indent=2))
def main():
 p=argparse.ArgumentParser();s=p.add_subparsers(dest='cmd',required=True)
 q=s.add_parser('prepare');q.add_argument('--id',required=True);q.add_argument('--manifest',required=True);q.add_argument('--xy',nargs=2,type=int,required=True)
 q=s.add_parser('request');q.add_argument('--id',required=True);q.add_argument('--parameters',required=True)
 q=s.add_parser('ingest');q.add_argument('--id',required=True);q.add_argument('--source',required=True);q.add_argument('--receipt',required=True)
 q=s.add_parser('assemble');q.add_argument('--config',required=True)
 args=p.parse_args();globals()[args.cmd](args)
if __name__=='__main__':main()

