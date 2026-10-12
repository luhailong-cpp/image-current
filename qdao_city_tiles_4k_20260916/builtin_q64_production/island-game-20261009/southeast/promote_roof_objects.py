from workflow import *
from PIL import Image
import numpy as np,sys,shutil,subprocess
proposal=Path(sys.argv[1]);d=read(proposal)
pairs=[('r09_c11','v04',-4096),('r09_c12','v08',0)]
for i,(tid,rev,tilex) in enumerate(pairs):
 o=d['outputs'][i];trial=Path(o['file']);base=Path(o['base']);assert sha(trial)==o['sha256'] and sha(base)==o['baseSha256'];assert sha(Path(o['sourceID']))==o['sourceIDSha256']
 arr=np.asarray(Image.open(trial).convert('RGB'));assert arr.shape==(4096,4096,3);owners=np.zeros((4096,4096),np.uint16);cover=np.zeros((4096,4096),np.uint8);sources=[]
 def add(file,expected,offset):
  assert sha(Path(file))==expected
  k=(str(file),tuple(offset))
  for q in sources:
   if (q['file'],tuple(q['originInTile']))==k:return q['id']
  q={'id':len(sources)+1,'file':str(file),'sha256':expected,'originInTile':offset};sources.append(q);return q['id']
 for p in read(Path(str(base)+'.generation.json'))['contributions']:
  x0,y0,x1,y1=p['destinationBox'];sx,sy,_,_=p['sourceCrop'];n=add(p['file'],p['sha256'],[x0-sx,y0-sy]);owners[y0:y1,x0:x1]=n;cover[y0:y1,x0:x1]+=1
 assert np.all(cover==1)
 overlay=np.asarray(Image.open(o['sourceID']))
 for job in d['jobs']:
  assert sha(Path(job['mask']))==job['maskSha256'];origin=job['originRelativeR09c12'];n=add(job['source'],job['sourceSha256'],[origin[0]-tilex,origin[1]]);owners[overlay==job['id']]=n
 assert np.all(owners>0)
 replay=np.zeros_like(arr);errors=[];active=[]
 for q in sources:
  ys,xs=np.where(owners==q['id'])
  if not len(ys):continue
  native=Path(q['file']);narr=np.asarray(Image.open(native).convert('RGB'));ox,oy=q['originInTile'];nx,ny=xs-ox,ys-oy
  assert nx.min()>=0 and ny.min()>=0 and nx.max()<narr.shape[1] and ny.max()<narr.shape[0]
  replay[ys,xs]=narr[ny,nx];mismatch=int(np.count_nonzero(np.any(replay[ys,xs]!=arr[ys,xs],axis=1)));q['selectedPixels']=len(ys);q['mismatchedPixels']=mismatch;q['nativeSize']=[narr.shape[1],narr.shape[0]];assert q['nativeSize']==[1254,1254];active.append(q)
 assert np.array_equal(replay,arr)
 folder=ROOT/'qa'/f'{tid}-{rev}';folder.mkdir(exist_ok=True);idfile=folder/'source-id.png';Image.fromarray(owners).save(idfile)
 out=ROOT/'tiles'/f'{tid}.candidate-{rev}.png';assert not out.exists();shutil.copy2(trial,out);assert sha(out)==sha(trial)
 rec={'file':str(out),'sha256':sha(out),'width':4096,'height':4096,'generatedAt':now(),'operation':'Exact native source ownership; hard 0/1 masks select whole roof objects. Original RGB, coordinates and source pixels remain unchanged; no resampling or blending.','sources':active,'sourceID':str(idfile),'sourceIDSha256':sha(idfile),'sourceIdRule':'For pixel (x,y) with source id k, copy native RGB at (x-originInTile[0],y-originInTile[1]).','proposal':str(proposal),'proposalSha256':sha(proposal),'base':str(base),'baseSha256':sha(base),'fullCoverage':True,'allContributionsPixelExact':True,'mismatchedPixelCount':0,'totalReplayedPixels':4096*4096,'actualModel':None,'actualQuality':None,'status':'pending_internal_and_shared_boundary_final_review','formalAccepted':False}
 write(Path(str(out)+'.generation.json'),rec);write(folder/'source-audit.json',rec)
 spec=ROOT/f'qa-spec-{tid}.json';write(spec,{'tile':tid,'seamShifts':[] if tid=='r09_c11' else [{'subrow':4,'afterSubcolumn':2,'deltaPixels':-115}]});subprocess.run([sys.executable,str(ROOT/'qa_from_candidate.py'),str(spec),rev],check=True)
 old=ROOT/'tiles'/('r09_c11.candidate.png' if tid=='r09_c11' else 'r09_c12.candidate-v02.png');oldim=Image.open(old).convert('RGB');newim=Image.open(out).convert('RGB');seams=read(folder/'seams.json');replays=[]
 for entry in seams['entries']:replays.append({'id':entry['id'],'unchanged':oldim.crop(entry['sourceCrop']).tobytes()==newim.crop(entry['sourceCrop']).tobytes(),'file':entry['file']})
 for rr in range(1,4):
  for cc in range(1,4):
   box=[cc*1024-256,rr*1024-256,cc*1024+256,rr*1024+256];jp=folder/f'junction_{rr}{cc}.png';newim.crop(box).save(jp);replays.append({'id':f'junction_{rr}{cc}','file':str(jp),'unchanged':oldim.crop(box).tobytes()==newim.crop(box).tobytes()})
 newim.resize((1024,1024),Image.Resampling.LANCZOS).save(folder/'preview.png')
 write(folder/'prior-reviewed-pixel-replay.json',{'base':str(old),'baseSha256':sha(old),'candidate':str(out),'candidateSha256':sha(out),'entries':replays,'changedEntries':[q['id'] for q in replays if not q['unchanged']]})
 print(tid,sha(out),'sourceCount',len(active),'changed',[q['id'] for q in replays if not q['unchanged']])

