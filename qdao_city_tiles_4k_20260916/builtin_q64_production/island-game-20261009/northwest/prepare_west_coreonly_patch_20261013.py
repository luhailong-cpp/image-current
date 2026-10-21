"""Prepare actual final-tile native anchors for west continuation. Guide-only coordinate crop/paste."""
from pathlib import Path
import argparse,json
from PIL import Image
import prepare_zone_patch as prep
import assemble_connected_tiles as connected
import apply_native_tile_repair as repair
import sys
Z=Path(__file__).resolve().parent
sys.path.insert(0,str(Z/'qa'))
import run_cross_with_strict_memo as strict_memo
p=argparse.ArgumentParser()
for n in ('tile-row','tile-col','subrow','subcol'):p.add_argument('--'+n,type=int,required=True)
p.add_argument('--attempt',required=True)
for n in prep.DIRECTIONS:p.add_argument('--'+n)
p.add_argument('--top-final');p.add_argument('--right-final');p.add_argument('--top-record');p.add_argument('--right-record')
a=p.parse_args();a.output_dir=None
original=prep.load_neighbor
def load(stem,direction,target,contract):
 final=a.top_final if direction=='top' else a.right_final if direction=='right' else None
 if not final:return original(stem,direction,target,contract)
 base=(Z/final).resolve(); explicit_record=a.top_record if direction=='top' else a.right_record
 rec=(Z/explicit_record).resolve() if explicit_record else base.with_suffix('.native-repair.json')
 if not rec.exists():rec=base.with_suffix('.assembly.json')
 cache=Z/'guides'/f'{target["tile"]}_{base.stem}_{direction}_anchors.json'
 if not cache.exists():
  padded,proof=connected.reconstruct_padded(base,rec);items=[]
  for slot in range(1,5):
   sr,sc=(4,slot) if direction=='top' else (slot,1)
   box=[(sc-1)*1024,(sr-1)*1024,(sc-1)*1024+1254,(sr-1)*1024+1254]
   path=Z/'guides'/f'{target["tile"]}_{base.stem}_{direction}_s{sr:02d}_{sc:02d}.native-anchor.png'
   assert not path.exists()
   Image.fromarray(padded[box[1]:box[3],box[0]:box[2]]).save(path)
   x,y=proof['tileOrigin'];gb=[x+box[0]-115,y+box[1]-115,x+box[2]-115,y+box[3]-115]
   items.append({**repair.file_info(path),'nativeSize':[1254,1254],'slot':slot,'globalBox':gb,'coreBox':[gb[0]+115,gb[1]+115,gb[2]-115,gb[3]-115],'derivedFrom':{'image':proof['image'],'record':proof['record'],'rootAssembly':proof['rootAssembly'],'paddedCropBox':box},'resized':False})
  cache.write_text(json.dumps({'sourceProof':proof,'anchors':items,'purpose':'guide-only exact final tile core with original verified halo; no art synthesis'},indent=2)+'\n',encoding='utf8')
 data=json.loads(cache.read_text(encoding='utf8'));assert data['sourceProof']['image']==repair.file_info(base) and data['sourceProof']['record']==repair.file_info(rec)
 item=next(x for x in data['anchors'] if x['slot']==(a.subcol if direction=='top' else a.subrow));repair.pinned(item,Z,'current final anchor')
 b=item['globalBox'];t=target['globalBox'];dx,dy=prep.OFFSETS[direction]
 assert item['coreBox'][:2]==[target['coreBox'][0]+dx,target['coreBox'][1]+dy]
 common=[max(t[0],b[0]),max(t[1],b[1]),min(t[2],b[2]),min(t[3],b[3])]
 crop=[common[0]-b[0],common[1]-b[1],common[2]-b[0],common[3]-b[1]];dest=[common[0]-t[0],common[1]-t[1]]
 if direction=='top':
  crop[3]=1139;common[3]-=115
 if direction=='right':
  crop[0]=115;dest[0]+=115;common[0]+=115
 item={**item,'stem':stem,'direction':direction,'role':direction+' adjacent verified final tile actual native edge, not stale original raw patch','sourceZone':Z.name,'globalOverlapBox':common,'sourceCrop':crop,'destination':dest,'targetLocalBox':[dest[0],dest[1],dest[0]+crop[2]-crop[0],dest[1]+crop[3]-crop[1]],'sameTile':False,'coordinateEvidence':repair.file_info(cache),'finalTileRecord':repair.file_info(rec)}
 return item,Image.open(item['path']).convert('RGB')
prep.load_neighbor=load
print(json.dumps(prep.prepare(a),indent=2))


