from pathlib import Path
import json,sys,argparse
from PIL import Image
Z=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Z))
import cross_tile_native_repair as c
r=c.r
ap=argparse.ArgumentParser();ap.add_argument('--manifest',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
M=(Z/a.manifest).resolve();O=(Z/a.output).resolve();assert O.is_relative_to(Z);O.mkdir(exist_ok=False)
tiles,origin=c.load_manifest(M)
jobs={
 'shared_vertical_y4096-5120':[3856,4096,4336,5120],
 'shared_vertical_y5120-6144':[3856,5120,4336,6144],
 'shared_horizontal_x5120-6144':[5120,3856,6144,4336],
 'rail_bottom_margin':[3470,5640,4724,6090],
 'rail_left_margin':[3330,4596,3730,5850],
 'rail_right_margin':[4480,4596,4880,5850],
 'rail_top_margin':[3470,4430,4724,4830]
}
items=[]
for name,box in jobs.items():
 im=Image.new('RGB',(box[2]-box[0],box[3]-box[1]));parts=[];coverage=0
 for t in tiles:
  ox,oy=t['clusterOffset'];x0,y0=max(ox,box[0]),max(oy,box[1]);x1,y1=min(ox+4096,box[2]),min(oy+4096,box[3])
  if x1<=x0 or y1<=y0:continue
  assert r.file_info(Path(t['image']['path']))==t['image']
  with Image.open(t['image']['path']) as src:im.paste(src.convert('RGB').crop((x0-ox,y0-oy,x1-ox,y1-oy)),(x0-box[0],y0-box[1]))
  parts.append(dict(tileId=t['tileId'],source=t['image'],sourceBox=[x0-ox,y0-oy,x1-ox,y1-oy]));coverage+=(x1-x0)*(y1-y0)
 assert coverage==im.width*im.height
 p=O/f'{name}.png';im.save(p);items.append(dict(name=name,box=box,output=r.file_info(p),nativeSize=list(im.size),parts=parts))
c.write_json(O/'index.json',dict(operation='exact native same-coordinate changed-boundary diagnostic crops',isAiGeneration=False,resizing=False,manifest=r.file_info(M),items=items))
print(json.dumps(r.file_info(O/'index.json')))
