"""Tile-local helpers. Deterministic operations are guide/crop assembly only."""
from pathlib import Path
import sys,json,importlib.util
from PIL import Image
T=Path(__file__).resolve().parent; Z=T.parent
spec=importlib.util.spec_from_file_location('p',Z/'production_v2.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
ACTUAL=[('northwest','r05_c06','candidate/r05_c06-candidate-minimum-error-03d4dd9f7332.png','beb936eca2c223bf30e9d34717d8fd0e2254ee06cc0e1e25e4835a4138f44e39'),('north','r05_c07','candidate/r05_c07-candidate-localcut-e280bcf6d4f6.png','75374335df252505edbb301d18c17bca9434b8ac74852bdafa698eaba41f10ec'),('west','r06_c06','candidate/r06_c06-candidate-hard-077556c4fb59.png','105ed0953773073a1b336660887ab78e4f8ef145ec74285ac0f1bc3ae0a77595')]

def prepare(pid,version,edges):
 info=p.prepare('r06_c07',pid,version,edges);base=Image.open(info['guide']).convert('RGB');target=info['worldBox'];refs=[]
 enabled=p.parse_edges(edges)
 for side,tile,rel,digest in ACTUAL:
  if side=='northwest' and not {'north','west'}<=enabled:continue
  if side!='northwest' and side not in enabled:continue
  path=Z/tile/rel;box=p.tile_box(tile);intersection=p.overlap(target,box)
  if intersection is None:continue
  assert p.sha(path)==digest
  source=[intersection[0]-box[0],intersection[1]-box[1],intersection[2]-box[0],intersection[3]-box[1]];dest=[intersection[0]-target[0],intersection[1]-target[1],intersection[2]-target[0],intersection[3]-target[1]]
  with Image.open(path) as image:base.paste(image.crop(source),(dest[0],dest[1]))
  refs.append(dict(side=side,tile=tile,file=str(path),sha256=digest,sourceBox=source,targetBox=dest,sourceResampled=False))
 output=T/'layout-only'/f'{pid}_{version}.actual-final-guide.png';p.save_png(output,base)
 p.write_json(output.with_suffix('.png.derivation.json'),dict(file=str(output),sha256=p.sha(output),role='mixed native overlaps and actual final4096 neighbor pixels; layout elsewhere only; never production artwork',worldBox=target,baseGuide=dict(file=info['guide'],sha256=p.sha(info['guide'])),actualFinalAnchors=refs,operation='Exact same-world crop and paste, no resizing of actual anchors',sourceResampled=False,gameArt=False))
 print(json.dumps(dict(guide=str(output),worldBox=target,actualFinalAnchors=refs,nativeAnchors=info['nativeAnchors'])))

def qa(identifier):
 pid=identifier[:6];target=T/'native'/(identifier+'.png');ref=p.validate_native(target,T,pid);r=int(pid[1:3]);c=int(pid[4:6]);coords=p.coordinates('r06_c07');world=next(x for x in coords['patches'] if x['id']==pid)['coreWorldBox'];northwest={key:(tile,path,digest) for key,tile,path,digest in ACTUAL};pieces={}
 def native(role,rr,cc):
  npid=f's{rr:02d}_{cc:02d}';path=p.selected_path(T,npid)
  if path.exists():pieces[role]=(Image.open(path).convert('RGB').crop((115,115,1139,1139)),p.validate_native(path,T,npid))
 if r>1:native('north',r-1,c)
 else:
  tile,rel,digest=northwest['north'];path=Z/tile/rel;box=p.tile_box(tile);xy=[world[0]-box[0],3072,world[2]-box[0],4096];pieces['north']=(Image.open(path).convert('RGB').crop(xy),dict(file=str(path),sha256=digest,sourceCropLTRB=xy))
 if c>1:native('west',r,c-1)
 else:
  tile,rel,digest=northwest['west'];path=Z/tile/rel;xy=[3072,(r-1)*1024,4096,r*1024];pieces['west']=(Image.open(path).convert('RGB').crop(xy),dict(file=str(path),sha256=digest,sourceCropLTRB=xy))
 if r>1 and c>1:native('northwest',r-1,c-1)
 elif r==1 and c==1:
  tile,rel,digest=northwest['northwest'];path=Z/tile/rel;xy=[3072,3072,4096,4096];pieces['northwest']=(Image.open(path).convert('RGB').crop(xy),dict(file=str(path),sha256=digest,sourceCropLTRB=xy))
 elif r==1:
  tile,rel,digest=northwest['north'];path=Z/tile/rel;xy=[(c-2)*1024,3072,(c-1)*1024,4096];pieces['northwest']=(Image.open(path).convert('RGB').crop(xy),dict(file=str(path),sha256=digest,sourceCropLTRB=xy))
 else:
  tile,rel,digest=northwest['west'];path=Z/tile/rel;xy=[3072,(r-2)*1024,4096,(r-1)*1024];pieces['northwest']=(Image.open(path).convert('RGB').crop(xy),dict(file=str(path),sha256=digest,sourceCropLTRB=xy))
 pieces['target']=(Image.open(target).convert('RGB').crop((115,115,1139,1139)),ref)
 out=T/'qa'/'source-review'/identifier;out.mkdir(parents=True,exist_ok=False);defs={'north-seam':((1024,320),[('north',[0,864,1024,1024],[0,0]),('target',[0,0,1024,160],[0,160])]),'west-seam':((320,1024),[('west',[864,0,1024,1024],[0,0]),('target',[0,0,160,1024],[160,0])]),'northwest-junction':((320,320),[('northwest',[864,864,1024,1024],[0,0]),('north',[0,864,160,1024],[160,0]),('west',[864,0,1024,160],[0,160]),('target',[0,0,160,160],[160,160])])};crops=[]
 for name,(size,parts) in defs.items():
  if any(role not in pieces for role,_,_ in parts):continue
  image=Image.new('RGB',size)
  for role,box,xy in parts:image.paste(pieces[role][0].crop(box),xy)
  path=out/(name+'.png');p.save_png(path,image);crops.append(dict(file=str(path),sha256=p.sha(path),parts=parts,nativePixelScale=1,sourceResampled=False))
 p.write_json(out/'manifest.json',dict(source=ref,neighbors={k:v[1] for k,v in pieces.items() if k!='target'},crops=crops,actuallyViewed=False,formalAccepted=False));print(json.dumps(dict(source=ref,crops=crops)))

if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare(*sys.argv[2:])
 elif sys.argv[1]=='qa':qa(sys.argv[2])

