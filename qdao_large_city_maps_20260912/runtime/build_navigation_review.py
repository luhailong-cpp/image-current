from pathlib import Path
import base64,hashlib,json
from PIL import Image,ImageDraw
ROOT=Path(r'E:\work\image\qdao_large_city_maps_20260912\runtime')
CLIENT=Path(r'E:\work\mmorpg-client\Assets\Resources\World\FestivalRegions')
regions=[]
for region in ['penglai','donghai','lanxian']:
 doc=json.loads((ROOT/f'{region}-navigation.json').read_text(encoding='utf-8'))
 mask_path=CLIENT/region/'walkmask.txt';raw=base64.b64decode(mask_path.read_text(encoding='ascii').strip(),validate=True)
 digest=hashlib.sha256(raw).hexdigest()
 assert len(raw)==2813 and digest==doc['decoded_mask_sha256'] and raw[-1]&15==0
 assert not doc['failed_checks'] and all(doc['validation'].values())
 panels=[];paths=[]
 for atm in ['day','festival']:
  source=Image.open(ROOT/f'{region}-{atm}-walkmask-overlay.png').convert('RGB')
  panel=Image.new('RGB',(1254,1290),(22,26,32));panel.paste(source,(0,36));ImageDraw.Draw(panel).text((16,10),f'{region.upper()} / {atm.upper()} : green = complete safe 2 m cells',fill='white');panels.append(panel)
  route_panel=panel.copy();d=ImageDraw.Draw(route_panel)
  for i,record in enumerate(doc['landmarks']):
   color=[(255,230,65),(255,105,220),(40,220,255),(255,130,55)][i%4]
   points=[((x+.5)*1254/150,(y+.5)*1254/150+36) for x,y in record['path_cells']]
   d.line(points,fill=color,width=2)
   x,y=record['pixel'];d.ellipse((x-4,y+32,x+4,y+40),fill=color,outline='black');d.text((x+6,y+30),str(i+1),fill='white',stroke_width=1,stroke_fill='black')
  paths.append(route_panel)
 for suffix,images in [('navigation-side-by-side',panels),('paths-side-by-side',paths)]:
  contact=Image.new('RGB',(2508,1290));contact.paste(images[0],(0,0));contact.paste(images[1],(1254,0));contact.save(ROOT/f'{region}-{suffix}.jpg',quality=91,subsampling=0)
 regions.append({'region':region,'status':'passed','decoded_mask_sha256':digest,'base64_text_sha256':hashlib.sha256(mask_path.read_bytes()).hexdigest(),'walkable_cells':doc['walkable_cells'],'walkable_percent_full_canvas':doc['walkable_percent'],'walkable_world_square_metres':doc['walkable_cells']*4,'landmark_route_count':len(doc['landmarks']),'blocked_probe_count':len(doc['blocked_probes']),'spawn_world':doc['spawnWorld'],'spawn_cell':doc['spawn_cell'],'review_images':[f'{region}-navigation-side-by-side.jpg',f'{region}-paths-side-by-side.jpg']})
report={'schema_version':1,'status':'passed','review_date':'2026-09-13','mask_locked':True,'visual_review':'Native 1254-pixel day and festival artwork and 100-pixel-grid navigation overlays were visually reviewed for all six maps, plus enlarged harbor, plaza, fishing-rack crops. The broad central plazas are fully represented by floor polygons, not just path centerlines.','changes':['Penglai: open the actual descending harbor staircase and upper stone dock, remove cargo/awning silhouettes from movement; relocate the former harbor probe away from cargo.','Lanxian: extend the wide central paved plaza perimeter and add two reachable pavement probes.','Donghai: refine front-shop and drying-rack contours to keep genuinely visible pavement open.'],'limitations':['Full-canvas walkable percentage includes the surrounding sea, mountains, forest and all opaque roofs; it is not a percentage of visible pavement.','Southern harbor and inner drying-rack pockets that cannot connect through complete safe 2 m cells are excluded rather than forcing paths through props.','Opaque baked gate roofs remain blocked. Traversal under a roof requires an independent foreground/occlusion implementation; no roof cells were made walkable merely to connect exterior courts.'],'geometry_contract':{'grid':[150,150],'cell_size_world_metres':2,'decoded_bytes':2813,'packing':'MSB first, row zero north, four zero pad bits','entire_cell_must_fit_safe_floor':True,'source_pixel_margin':1},'landmark_route_count':sum(r['landmark_route_count'] for r in regions),'blocked_probe_count':sum(r['blocked_probe_count'] for r in regions),'regions':regions}
(ROOT/'navigation-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
