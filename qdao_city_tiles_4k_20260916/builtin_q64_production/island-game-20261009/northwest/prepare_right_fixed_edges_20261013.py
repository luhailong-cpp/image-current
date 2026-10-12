from pathlib import Path
from types import SimpleNamespace
import argparse,json
from PIL import Image
import assemble_connected_tiles as connected
import apply_native_tile_repair as repair
import prepare_zone_patch as prepare
Z=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--row',type=int,required=True);p.add_argument('--col',type=int,required=True);p.add_argument('--attempt',default='a01')
for di in ('left','right','top','bottom'):p.add_argument('--'+di)
a=p.parse_args();assert 1<=a.row<=4 and 1<=a.col<=4
fixed={}
for di,tile,ver,index in [('top','r06_c04','v10',a.col),('left','r07_c03','v7',a.row)]:
 if (di=='top' and a.row!=1) or (di=='left' and a.col!=1):continue
 base=Z/'tiles'/f'{tile}_candidate-{ver}_4096.png';record=base.with_suffix('.native-repair.json')
 expected={'r06_c04':'566a48cc76b3c43c5a339ac39a753663c28696871d832650ab7ce3cb266d0aa8','r07_c03':'ca295176c0b35366814428d79240195b8afa7e679fd6c74b4711f5e82b13fc53'}[tile]
 assert repair.file_info(base)['sha256']==expected
 cache=Z/'guides'/f'r07_c04_fixed_{di}_{tile}_{ver}_anchors_20261013.json'
 if not cache.exists():
  padded,proof=connected.reconstruct_padded(base,record);anchors=[]
  for i in range(1,5):
   box=[(i-1)*1024,3072,(i-1)*1024+1254,4326] if di=='top' else [3072,(i-1)*1024,4326,(i-1)*1024+1254]
   path=Z/'guides'/f'r07_c04_fixed_{di}_{tile}_{ver}_{i:02d}_anchor_20261013.png';assert not path.exists()
   pixels=padded[box[1]:box[3],box[0]:box[2]];assert pixels.shape==(1254,1254,3);Image.fromarray(pixels).save(path)
   x,y=proof['tileOrigin'];gb=[x+box[0]-115,y+box[1]-115,x+box[2]-115,y+box[3]-115]
   anchors.append({**repair.file_info(path),'nativeSize':[1254,1254],'index':i,'globalBox':gb,'kind':'verifiedTileCoreWithOriginalNativeHalo','role':f'{di} current {tile} {ver} exact edge anchor; reference only','derivedFrom':{'image':proof['image'],'record':proof['record'],'rootAssembly':proof['rootAssembly'],'paddedCropBox':box},'resizing':False,'registration':False,'pixelSynthesis':False})
  with cache.open('x',encoding='utf8') as f:json.dump({'sourceProof':proof,'anchors':anchors,'operation':'same-coordinate native reference crop'},f,indent=2)
 data=json.loads(cache.read_text());assert data['sourceProof']['image']==repair.file_info(base) and data['sourceProof']['record']==repair.file_info(record)
 anchor=next(i for i in data['anchors'] if i['index']==index);repair.pinned(anchor,Z,'fixed exact anchor')
 fixed[di]=(anchor,cache);setattr(a,di,'fixed-'+di)
original=prepare.load_neighbor
def load(stem,direction,target,contract):
 if stem!='fixed-'+direction:return original(stem,direction,target,contract)
 anchor,cache=fixed[direction];b=target['globalBox']
 crop=[0,1024,1254,1139] if direction=='top' else [1024,0,1139,1254]
 box=[0,0,1254,115] if direction=='top' else [0,0,115,1254]
 entry={**anchor,'direction':direction,'sourceZone':'northwest','sourceCrop':crop,'destination':[0,0],'targetLocalBox':box,'globalOverlapBox':[b[0],b[1],b[0]+box[2],b[1]+box[3]],'coordinateEvidence':repair.file_info(cache),'resized':False,'sameTile':False,'haloPolicy':'Only verified adjacent formal core edge115 used; old outside-core halo excluded. Orthogonal 115 corner is reference halo and replaced by top edge when present.'}
 return entry,Image.open(anchor['path']).convert('RGB')
prepare.load_neighbor=load
result=prepare.prepare(SimpleNamespace(tile_row=7,tile_col=4,subrow=a.row,subcol=a.col,attempt=a.attempt,left=a.left,right=a.right,top=a.top,bottom=a.bottom,output_dir=None))
print(json.dumps({'guide':result['guide']['path'],'input':result['input'],'references':result['references']}))

