from pathlib import Path
from PIL import Image
import json,sys,subprocess,os
from workflow import ROOT,read,write,sha,now,patch
PROG=ROOT/'production-resume-wall-20261013.json'
Q=ROOT/'qa'/'wall-resume-20261013'
Q.mkdir(exist_ok=True)
cmd=sys.argv[1]
if cmd=='prepare':
 pid,v,desc,*neigh=sys.argv[2:]
 if neigh:
  guide=ROOT/'guides'/f'{pid}.native-context-{v}.png'
  assert not guide.exists(),str(guide)
  p=patch(pid);box=p['nativeGlobalBox']
  base=ROOT/'guides'/f'{pid}.layout-only.png'
  im=Image.open(base).convert('RGB');parts=[{'file':str(base),'sha256':sha(base),'role':'layout-only, not final pixels'}]
  for name in neigh:
   src=ROOT/'native'/name;rec=read(Path(str(src)+'.generation.json'));nb=rec['coordinate']['nativeGlobalBox']
   inter=[max(box[0],nb[0]),max(box[1],nb[1]),min(box[2],nb[2]),min(box[3],nb[3])]
   assert inter[0]<inter[2] and inter[1]<inter[3]
   crop=[inter[0]-nb[0],inter[1]-nb[1],inter[2]-nb[0],inter[3]-nb[1]];dest=[inter[0]-box[0],inter[1]-box[1]]
   im.paste(Image.open(src).convert('RGB').crop(crop),dest)
   parts.append({'file':str(src),'sha256':sha(src),'sourceCrop':crop,'destination':dest})
  im.save(guide);write(Path(str(guide)+'.generation.json'),{'file':str(guide),'sha256':sha(guide),'derivedFrom':parts,'nativeGlobalBox':box,'usableAsFinalArt':False})
 env=dict(os.environ,ISLAND_PROGRESS_FILE=PROG.name)
 out=subprocess.run([sys.executable,str(ROOT/'request.py'),pid,v,desc],env=env,capture_output=True,text=True,check=True)
 args=json.loads(out.stdout);write(ROOT/'prompts'/f'{pid}_{v}.args.json',args)
 print(json.dumps({'pid':pid,'args':str(ROOT/'prompts'/f'{pid}_{v}.args.json'),'guide':args['referenced_image_paths'][0]}))
elif cmd=='check':
 pid,v,*neigh=sys.argv[2:];src=ROOT/'native'/f'{pid}_{v}.png';im=Image.open(src).convert('RGB');assert im.size==(1254,1254);p=patch(pid);b=p['coreGlobalBox'];out=[]
 for name in neigh:
  ns=ROOT/'native'/name;ni=Image.open(ns).convert('RGB');nb=read(Path(str(ns)+'.generation.json'))['coordinate']['coreGlobalBox']
  if nb[0]==b[2] and nb[1]==b[1]:
   direction='E';e=Image.new('RGB',(512,1024));e.paste(im.crop((883,115,1139,1139)),(0,0));e.paste(ni.crop((115,115,371,1139)),(256,0))
  elif nb[2]==b[0] and nb[1]==b[1]:
   direction='W';e=Image.new('RGB',(512,1024));e.paste(ni.crop((883,115,1139,1139)),(0,0));e.paste(im.crop((115,115,371,1139)),(256,0))
  elif nb[3]==b[1] and nb[0]==b[0]:
   direction='N';e=Image.new('RGB',(1024,512));e.paste(ni.crop((115,883,1139,1139)),(0,0));e.paste(im.crop((115,115,1139,371)),(0,256))
  elif nb[1]==b[3] and nb[0]==b[0]:
   direction='S';e=Image.new('RGB',(1024,512));e.paste(im.crop((115,883,1139,1139)),(0,0));e.paste(ni.crop((115,115,1139,371)),(0,256))
  else:continue
  dest=Q/f'{pid}-{v}-{direction}.png';assert not dest.exists(),str(dest);e.save(dest)
  out.append({'direction':direction,'file':str(dest),'sha256':sha(dest),'source':[{'file':str(src),'sha256':sha(src)},{'file':str(ns),'sha256':sha(ns)}],'operation':'unscaled adjacent 1024-core pixel crops 256 pixels each side','status':'pending_visual_review'})
 manifest=Q/f'{pid}-{v}-review.json';write(manifest,{'native':str(src),'sha256':sha(src),'edges':out,'status':'pending_visual_review','actualModel':None});print(json.dumps({'file':str(manifest),'edges':out}))
elif cmd=='select':
 pid,v,status,note=sys.argv[2:];f=ROOT/'native'/f'{pid}_{v}.png';d=read(PROG)
 d.setdefault('generated',{})[pid]={'file':str(f),'sha256':sha(f),'version':v,'status':status,'note':note,'reviewedAt':now()}
 d['generatedNativeCount']=len(d['generated']);d['updatedAt']=now();d['currentTile']=pid[:7];d['status']='active_builtin_native_continuation';d['inFlight']=False
 write(PROG,d);print(json.dumps({'selectedCount':sum(x['status']=='quick_layout_and_edges_passed' for x in d['generated'].values()),'pid':pid}))

