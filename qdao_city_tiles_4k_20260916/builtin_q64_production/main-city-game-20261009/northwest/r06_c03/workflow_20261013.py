"""Tile-local built-in production using actual final north and east pixels."""
from pathlib import Path
import sys,json,importlib.util
from PIL import Image
T=Path(__file__).resolve().parent;Z=T.parent
spec=importlib.util.spec_from_file_location('p',Z/'production_v2.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
ACTUAL=[('north','r05_c03','r05_c03/candidate/r05_c03-candidate-hard-80982c249bee.png','8705aba979d280b2e3e90767b54882b8d867027f1242de4a452a214db0a61053'),('east','r06_c04','joint-2x2-r05_c04-r06_c05/deeb69ed9f705a70/tiles/r06_c04-joint-4096.png','493e896f75ebe6188bc83d8359af92267ec9084132ad5631392b5a074e097282')]
def prepare(pid,version):
 info=p.prepare('r06_c03',pid,version,'north,east');base=Image.open(T/'layout-only'/(pid+'.layout-only.png')).convert('RGB');target=info['worldBox'];refs=[]
 for anchor in p.read(info['derivation'])['nativeNeighbors']:
  if anchor['tile']!='r06_c03':continue
  with Image.open(anchor['file']) as im:base.paste(im.crop(anchor['sourceBox']),anchor['targetBox'][:2])
 for side,tile,rel,digest in ACTUAL:
  path=Z/rel;assert p.sha(path)==digest;box=p.tile_box(tile);intersection=p.overlap(target,box)
  if intersection is None:continue
  source=[intersection[0]-box[0],intersection[1]-box[1],intersection[2]-box[0],intersection[3]-box[1]];dest=[intersection[0]-target[0],intersection[1]-target[1],intersection[2]-target[0],intersection[3]-target[1]]
  base.paste(Image.open(path).convert('RGB').crop(source),dest[:2]);refs.append(dict(side=side,tile=tile,file=str(path),sha256=digest,sourceBox=source,targetBox=dest,sourceResampled=False))
 path=T/'layout-only'/f'{pid}_{version}.actual-final-guide.png';p.save_png(path,base);p.write_json(path.with_suffix('.png.derivation.json'),dict(file=str(path),sha256=p.sha(path),role='layout-only with exact native internal and actual final4096 neighbor anchors; never production art',gameArt=False,worldBox=target,actualFinalAnchors=refs,internalGuide=info,sourceResampled=False))
 print(json.dumps(dict(guide=str(path),anchors=refs,worldBox=target)))
def qa(identifier):
 pid=identifier[:6];target=T/'native'/(identifier+'.png');ref=p.validate_native(target,T,pid);r=int(pid[1:3]);c=int(pid[4:6]);pieces={};world=next(x for x in p.coordinates('r06_c03')['patches'] if x['id']==pid)['coreWorldBox']
 def native(role,rr,cc):
  npid=f's{rr:02d}_{cc:02d}';path=p.selected_path(T,npid)
  if path.exists():pieces[role]=(Image.open(path).convert('RGB').crop((115,115,1139,1139)),p.validate_native(path,T,npid))
 if r>1:native('north',r-1,c)
 else:
  path=Z/ACTUAL[0][2];xy=[(c-1)*1024,3072,c*1024,4096];pieces['north']=(Image.open(path).convert('RGB').crop(xy),dict(file=str(path),sha256=p.sha(path),sourceCropLTRB=xy))
 if c<4:native('east',r,c+1)
 else:
  path=Z/ACTUAL[1][2];xy=[0,(r-1)*1024,1024,r*1024];pieces['east']=(Image.open(path).convert('RGB').crop(xy),dict(file=str(path),sha256=p.sha(path),sourceCropLTRB=xy))
 if r>1 and c<4:native('northeast',r-1,c+1)
 elif r==1 and c<4:
  path=Z/ACTUAL[0][2];xy=[c*1024,3072,(c+1)*1024,4096];pieces['northeast']=(Image.open(path).convert('RGB').crop(xy),dict(file=str(path),sha256=p.sha(path),sourceCropLTRB=xy))
 elif r>1:
  path=Z/ACTUAL[1][2];xy=[0,(r-2)*1024,1024,(r-1)*1024];pieces['northeast']=(Image.open(path).convert('RGB').crop(xy),dict(file=str(path),sha256=p.sha(path),sourceCropLTRB=xy))
 pieces['target']=(Image.open(target).convert('RGB').crop((115,115,1139,1139)),ref);out=T/'qa'/'source-review'/identifier;out.mkdir(parents=True,exist_ok=False)
 defs={'north-seam':((1024,320),[('north',[0,864,1024,1024],[0,0]),('target',[0,0,1024,160],[0,160])]),'east-seam':((320,1024),[('target',[864,0,1024,1024],[0,0]),('east',[0,0,160,1024],[160,0])]),'northeast-junction':((320,320),[('north',[864,864,1024,1024],[0,0]),('northeast',[0,864,160,1024],[160,0]),('target',[864,0,1024,160],[0,160]),('east',[0,0,160,160],[160,160])])};crops=[]
 for name,(size,parts) in defs.items():
  if any(role not in pieces for role,_,_ in parts):continue
  image=Image.new('RGB',size)
  for role,box,xy in parts:image.paste(pieces[role][0].crop(box),xy)
  path=out/(name+'.png');p.save_png(path,image);crops.append(dict(file=str(path),sha256=p.sha(path),parts=parts,nativePixelScale=1,sourceResampled=False))
 p.write_json(out/'manifest.json',dict(source=ref,neighbors={k:v[1] for k,v in pieces.items() if k!='target'},crops=crops,actuallyViewed=False,formalAccepted=False));print(json.dumps(dict(source=ref,crops=len(crops))))
if sys.argv[1]=='prepare':prepare(*sys.argv[2:])
elif sys.argv[1]=='qa':qa(sys.argv[2])
elif sys.argv[1]=='request':print(json.dumps(p.record_request('r06_c03',sys.argv[2],T/'planned'/(sys.argv[2]+'.parameters.json'))))
elif sys.argv[1]=='review':
 identifier=sys.argv[2];note=sys.argv[3];status=sys.argv[4] if len(sys.argv)>4 else 'passed_available_native_source_review';out=T/'qa/source-review'/identifier;m=p.read(out/'manifest.json');record=dict(status=status,source=m['source'],actuallyViewed=True,viewDetail='original',viewedNative=True,crops=[dict(file=x['file'],sha256=x['sha256'],actuallyViewed=True,verdict='pass' if status.startswith('passed') else 'needs_repair') for x in m['crops']],notes=note,fullTileInternalQA=False,formalAccepted=False,reviewer='/root/resume_r06_c07_finish');p.write_json(out/'review.json',record)
 if status.startswith('passed'):print(json.dumps(p.record_selection('r06_c03',identifier[:6],identifier,note,str(out/'review.json'))))
