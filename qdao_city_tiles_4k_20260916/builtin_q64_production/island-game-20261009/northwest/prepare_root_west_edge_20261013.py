from pathlib import Path
from types import SimpleNamespace
import argparse,json
from PIL import Image
import assemble_connected_tiles as connected
import apply_native_tile_repair as repair
import prepare_zone_patch as prep
Z=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--row',type=int,required=True);p.add_argument('--col',type=int,required=True);p.add_argument('--attempt',required=True)
for di in prep.DIRECTIONS:p.add_argument('--'+di)
a=p.parse_args();fixed=None
if a.col==4:
 base=Z/'tiles/r03_c02_candidate-v7_4096.png';record=base.with_suffix('.native-repair.json')
 assert repair.file_info(base)['sha256']=='8656bb1a4e07b91711d60ad68f1225abe27667c3647db43d07fa9f3f6a8a0bfa'
 cache=Z/'guides/r03_c01_fixed_right_r03_c02_v7_anchors_20261013.json'
 if not cache.exists():
  padded,proof=connected.reconstruct_padded(base,record);anchors=[]
  for i in range(1,5):
   box=[0,(i-1)*1024,1254,(i-1)*1024+1254];path=Z/'guides'/f'r03_c01_fixed_right_r03_c02_v7_{i:02d}_anchor_20261013.png';assert not path.exists()
   Image.fromarray(padded[box[1]:box[3],box[0]:box[2]]).save(path)
   x,y=proof['tileOrigin'];gb=[x+box[0]-115,y+box[1]-115,x+box[2]-115,y+box[3]-115]
   anchors.append({**repair.file_info(path),'nativeSize':[1254,1254],'index':i,'globalBox':gb,'derivedFrom':{'image':proof['image'],'record':proof['record'],'rootAssembly':proof['rootAssembly'],'paddedCropBox':box},'resizing':False})
  with cache.open('x',encoding='utf8') as f:json.dump({'sourceProof':proof,'anchors':anchors},f,indent=2)
 data=json.loads(cache.read_text());assert data['sourceProof']['image']==repair.file_info(base) and data['sourceProof']['record']==repair.file_info(record)
 anchor=next(i for i in data['anchors'] if i['index']==a.row);repair.pinned(anchor,Z,'fixed-right formal core edge')
 fixed=(anchor,cache);a.right='fixed-right'
original=prep.load_neighbor
def load(stem,direction,target,contract):
 if stem!='fixed-right':return original(stem,direction,target,contract)
 anchor,cache=fixed;b=target['globalBox']
 entry={**anchor,'direction':'right','role':'current verified right formal core first115; old outside-core halo excluded','sourceZone':'northwest','sourceCrop':[115,0,230,1254],'destination':[1139,0],'targetLocalBox':[1139,0,1254,1254],'globalOverlapBox':[b[0]+1139,b[1],b[2],b[3]],'coordinateEvidence':repair.file_info(cache),'resized':False,'sameTile':False,'haloPolicy':'actual adjacent formal core115 only; orthogonal corners are original native reference halo'}
 return entry,Image.open(anchor['path']).convert('RGB')
prep.load_neighbor=load
r=prep.prepare(SimpleNamespace(tile_row=3,tile_col=1,subrow=a.row,subcol=a.col,attempt=a.attempt,left=a.left,right=a.right,top=a.top,bottom=a.bottom,output_dir=None))
print(json.dumps({'guide':r['guide']['path'],'input':r['input'],'references':r['references']}))
