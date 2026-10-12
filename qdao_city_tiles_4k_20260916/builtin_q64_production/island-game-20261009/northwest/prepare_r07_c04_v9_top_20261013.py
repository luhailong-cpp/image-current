from pathlib import Path
import argparse,json
from types import SimpleNamespace
from PIL import Image
import assemble_connected_tiles as connected
import apply_native_tile_repair as repair
import prepare_zone_patch as prepare
Z=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--col',type=int,required=True);p.add_argument('--left');p.add_argument('--right');p.add_argument('--attempt',default='a01');a=p.parse_args();assert a.col in range(1,5)
base=Z/'tiles/r06_c04_candidate-v9_4096.png';record=base.with_suffix('.native-repair.json');cache=Z/'guides/r07_c04_r06c04_v9_top_anchors.json'
if not cache.exists():
 padded,proof=connected.reconstruct_padded(base,record);anchors=[]
 for col in range(1,5):
  box=[(col-1)*1024,3072,(col-1)*1024+1254,4326]
  path=Z/'guides'/f'r07_c04_top_r06c04_v9_s04_{col:02d}.native-anchor.png';assert not path.exists()
  pixels=padded[box[1]:box[3],box[0]:box[2]];assert pixels.shape==(1254,1254,3);Image.fromarray(pixels).save(path)
  x,y=proof['tileOrigin'];gb=[x+(col-1)*1024-115,y+3072-115,x+(col-1)*1024+1139,y+4211]
  anchors.append({**repair.file_info(path),'nativeSize':[1254,1254],'column':col,'globalBox':gb,'kind':'verifiedTileCoreWithOriginalNativeHalo','role':'top adjacent current r06_c04 v9 exact core and archived original halo; reference only, not raw generation','derivedFrom':{'image':proof['image'],'record':proof['record'],'rootAssembly':proof['rootAssembly'],'paddedCropBox':box},'resizing':False,'registration':False,'pixelSynthesis':False})
 cache.write_text(json.dumps({'operation':'same-coordinate native reference crop; original halo and final verified tile core','sourceProof':proof,'anchors':anchors},indent=2)+'\n',encoding='utf-8')
data=json.loads(cache.read_text());assert data['sourceProof']['image']==repair.file_info(base) and data['sourceProof']['record']==repair.file_info(record)
anchor=next(i for i in data['anchors'] if i['column']==a.col);repair.pinned(anchor,Z,'exact top anchor');original=prepare.load_neighbor;sentinel=f'current-r06c04-v9-col{a.col}'
def load(stem,direction,target,contract):
 if stem!=sentinel:return original(stem,direction,target,contract)
 assert direction=='top' and target['globalBox'][0]==anchor['globalBox'][0] and target['globalBox'][1]==anchor['globalBox'][1]+1024
 b=target['globalBox'];entry={**anchor,'direction':'top','sourceZone':'northwest','sourceCrop':[0,1024,1254,1254],'destination':[0,0],'targetLocalBox':[0,0,1254,230],'globalOverlapBox':[b[0],b[1],b[2],b[1]+230],'coordinateEvidence':repair.file_info(cache),'resized':False,'sameTile':False}
 return entry,Image.open(anchor['path']).convert('RGB')
prepare.load_neighbor=load
result=prepare.prepare(SimpleNamespace(tile_row=7,tile_col=4,subrow=1,subcol=a.col,attempt=a.attempt,left=a.left,right=a.right,top=sentinel,bottom=None,output_dir=None))
print(json.dumps({'guide':result['guide']['path'],'input':result['input'],'references':result['references'],'anchorProof':repair.file_info(cache),'nativeGenerationPerformed':False}))
