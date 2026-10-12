from pathlib import Path
import json, base64, re, shutil, hashlib
from collections import deque
import numpy as np
from PIL import Image, ImageDraw
ROOT=Path(r'E:\work\image\tianyong_festival_hd_20260910')
OUT=ROOT/'runtime'; OUT.mkdir(exist_ok=True)
CLIENT=Path(r'E:\work\mmorpg-client')
# 在896像素审阅图上描出的地面边界，坐标按比例映射到6144原图。
regions={
'central':[(357,101),(538,101),(549,157),(551,214),(559,250),(557,324),(589,347),(621,387),(632,463),(597,497),(551,521),(517,544),(517,605),(528,647),(516,735),(504,754),(393,754),(378,737),(365,650),(376,605),(379,546),(327,531),(304,499),(265,483),(255,437),(266,383),(302,354),(332,331),(338,295),(339,249),(350,213)],
'north_entry':[(435,79),(463,79),(463,120),(435,120)],
'south_avenue':[(393,729),(504,729),(502,777),(477,788),(468,834),(511,846),(521,895),(367,895),(383,849),(423,832),(423,789),(397,782)],
'northwest':[(121,79),(275,79),(286,171),(283,218),(263,243),(169,242),(164,282),(86,310),(95,163)],
'northeast':[(614,80),(746,82),(782,149),(797,249),(703,248),(704,287),(631,280),(615,221),(605,167)],
'west_middle':[(83,288),(164,282),(267,287),(273,326),(251,366),(250,429),(249,482),(265,527),(157,552),(79,530),(57,424)],
'east_middle':[(639,286),(701,283),(795,289),(829,424),(811,528),(714,553),(632,538),(625,501),(648,465),(644,391),(624,335)],
'west_bottom':[(74,576),(137,576),(158,544),(283,575),(314,629),(306,692),(281,775),(91,777),(63,723)],
'east_bottom':[(631,575),(715,575),(715,541),(809,541),(836,727),(803,777),(611,777),(580,695),(582,634)],
'bridge_nw':[(276,194),(286,183),(305,177),(324,183),(342,195),(342,208),(325,197),(305,190),(286,196),(276,206)],
'bridge_ne':[(552,195),(568,184),(584,180),(602,186),(614,195),(614,206),(600,198),(584,192),(568,195),(552,209)],
'bridge_sw':[(303,677),(321,667),(341,665),(365,674),(378,687),(373,699),(356,686),(338,679),(319,682),(305,690)],
'bridge_se':[(516,682),(534,670),(552,665),(573,671),(591,683),(588,697),(569,683),(552,678),(535,684),(517,696)],
'west_gate_stairs':[(145,538),(175,538),(175,580),(134,580)],
'east_gate_stairs':[(722,521),(777,521),(795,577),(710,577)],
}
# 只阻挡实际建筑、围栏、灯座、水池和绿化；台阶和桥面保留通行。
blocks={
'main_hall':[(384,177),(505,176),(520,202),(517,236),(523,251),(518,294),(495,309),(401,309),(378,295),(377,235)],
'west_lamp':[(343,286),(359,286),(362,334),(340,334)],
'east_lamp':[(539,287),(551,287),(557,334),(535,334)],
'hall_west_garden':[(381,304),(420,305),(420,337),(385,337)],
'hall_east_garden':[(475,305),(513,305),(513,338),(475,338)],
'nw_stage1':[(153,80),(216,78),(238,95),(244,123),(229,141),(167,145),(149,129),(148,98)],
'nw_stage2':[(145,148),(222,146),(247,162),(251,203),(234,224),(164,229),(139,208),(134,174)],
'nw_pavilion':[(247,128),(286,125),(289,164),(247,166)],
'nw_willow':[(262,86),(302,87),(305,128),(279,150),(266,140)],
'west_temple':[(117,327),(195,325),(204,345),(198,382),(115,382),(107,350)],
'west_market1':[(87,369),(112,369),(119,398),(136,398),(139,434),(87,434)],
'west_market2':[(195,373),(229,374),(239,410),(234,438),(192,438)],
'west_market3':[(78,453),(112,449),(124,475),(118,507),(137,516),(137,545),(76,545)],
'west_market4':[(156,449),(178,449),(184,475),(183,511),(151,511)],
'west_market5':[(196,452),(231,452),(237,478),(235,515),(199,515)],
'west_willow':[(229,273),(253,269),(269,277),(270,304),(258,318),(232,308)],
'west_plaza_lantern':[(267,350),(279,350),(281,393),(263,394)],
'west_lower_temple':[(168,569),(261,568),(278,595),(278,623),(254,633),(164,625),(149,604)],
'west_fountain':[(175,635),(232,635),(246,659),(241,689),(220,710),(184,703),(163,685),(163,655)],
'west_lower_house':[(57,590),(96,590),(113,626),(109,660),(66,660),(53,638)],
'west_south_house':[(88,691),(123,691),(136,713),(133,743),(81,743),(82,716)],
'west_se_house':[(230,716),(278,716),(288,745),(286,774),(223,774),(212,743)],
'west_tree':[(269,628),(295,628),(295,653),(268,653)],
'west_tree2':[(124,633),(149,633),(150,679),(121,679)],
'ne_tower':[(684,76),(726,76),(734,110),(731,139),(714,152),(685,147),(680,121)],
'ne_house':[(622,65),(677,65),(682,88),(678,109),(616,109)],
'ne_round':[(714,143),(748,143),(762,168),(758,190),(738,205),(711,194),(700,177)],
'ne_shrine':[(661,184),(686,184),(695,206),(691,225),(662,227),(651,208)],
'ne_small':[(660,133),(679,133),(684,158),(657,165),(650,151)],
'east_temple':[(710,315),(782,313),(795,335),(786,369),(707,369),(699,341)],
'east_sundial':[(737,381),(767,379),(780,405),(774,431),(742,441),(725,424),(725,403)],
'east_shrine':[(665,360),(690,361),(705,394),(700,426),(665,426),(655,399)],
'east_gate':[(676,452),(715,454),(719,463),(778,455),(782,467),(819,457),(836,483),(829,517),(668,517),(665,484)],
'east_tree':[(643,266),(662,265),(673,291),(665,315),(640,315)],
'east_plaza_lantern':[(618,350),(629,350),(635,394),(614,394)],
'east_lower_shrine':[(586,587),(617,584),(632,608),(629,636),(581,636),(575,609)],
'east_lower_house1':[(679,615),(725,615),(737,636),(731,659),(677,659),(670,639)],
'east_lower_house2':[(780,615),(817,615),(829,640),(823,659),(778,659),(767,637)],
'east_pond':[(628,652),(681,654),(717,682),(731,722),(705,752),(669,775),(625,770),(594,747),(583,716),(597,680)],
'east_moon':[(734,697),(797,697),(815,732),(809,768),(730,770),(721,732)],
'south_west_lamp':[(377,676),(395,676),(397,726),(376,726)],
'south_east_lamp':[(500,676),(518,676),(519,726),(498,726)],
'south_west_tree':[(345,608),(378,605),(384,632),(374,650),(345,649)],
'south_east_tree':[(520,607),(554,607),(555,649),(521,648)],
'central_west_tree':[(320,500),(351,500),(361,541),(324,541)],
'central_east_tree':[(542,500),(573,500),(577,541),(539,541)],
'north_west_lamp':[(367,109),(384,109),(385,143),(363,143)],
'north_east_lamp':[(514,109),(531,109),(533,144),(512,144)],
}
# 更细小的植被/摆设用独立占地，不把道路截断。
for name,x,y,r in [('plaza_west_pot',397,536,10),('plaza_east_pot',500,537,10),('nw_trees',339,148,13),('ne_trees',553,148,13),('west_plaza_tree',311,495,12),('east_plaza_tree',583,495,12),('sw_pot',277,674,11),('sw_tree',147,740,12),('se_tree',672,594,16)]:
    blocks[name]=[(x-r,y-r),(x+r,y-r),(x+r,y+r),(x-r,y+r)]
# 南城门屋顶封闭，不让角色从贴图表面穿过门楼；入口落在城内大道。
regions['south_avenue']=[(393,714),(504,714),(504,741),(393,741)]
blocks.update({
'west_lamp_base':[(342.7,329.6),(357.8,329.6),(357.8,342.6),(342.7,342.6)],
'east_lamp_base':[(539.1,329.6),(552.9,329.6),(552.9,342.6),(539.1,342.6)],
'south_gate_roof':[(385,744),(512,744),(526,786),(505,819),(389,819),(374,786)],
'nw_small_shrine':[(93,228),(119,228),(125,250),(123,269),(90,269)],
'west_lower_stall':[(177,517),(243,517),(247,551),(179,551)],
'east_lower_house3':[(792,683),(839,681),(854,703),(846,727),(790,727),(781,704)],
'east_gate_sidelamp':[(788,412),(800,412),(804,448),(787,448)],
'west_plaza_barrel':[(171,406),(195,406),(195,434),(171,434)],
})
canvas=Image.new('L',(1792,1792)); d=ImageDraw.Draw(canvas)
for poly in regions.values(): d.polygon([(x*2,y*2) for x,y in poly],fill=255)
for poly in blocks.values(): d.polygon([(x*2,y*2) for x,y in poly],fill=0)
a=np.array(canvas.resize((150,150),Image.Resampling.BOX))>=180
# 从原画提取植物/水面色彩，只作多边形内的小型障碍补充，不生成任何画面。
original=np.array(Image.open(ROOT/'tianyong_city_master_preview_2048.png').convert('RGB')).astype(float)
r,g,b=original[:,:,0],original[:,:,1],original[:,:,2]
vegetation=((g>r*1.10)&(g>b*1.12)) | ((b>r*1.3)&(g>r*1.15))
coverage=np.array(Image.fromarray(vegetation.astype('uint8')*255).resize((150,150),Image.Resampling.BOX))
exempt=Image.new('L',(1792,1792)); ex=ImageDraw.Draw(exempt)
for name,poly in regions.items():
    if name.startswith('bridge_') or name.endswith('_gate_stairs'):
        ex.polygon([(x*2,y*2) for x,y in poly],fill=255)
a &= (coverage < 185) | (np.array(exempt.resize((150,150),Image.Resampling.BOX))>=100)
sx,sy=75,60
assert a[sy,sx], '出生点必须在实际地面'
seen=np.zeros_like(a); seen[sy,sx]=True;q=deque([(sx,sy)])
while q:
    x,y=q.popleft()
    for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
        u,v=x+dx,y+dy
        if 0<=u<150 and 0<=v<150 and a[v,u] and not seen[v,u]: seen[v,u]=1;q.append((u,v))
disconnected=int(np.sum(a & ~seen)); a=seen
probes={'spawn':(448,358.4),'plaza':(448,434),'north_avenue':(450,141),'west_north':(261,204),'east_north':(637,214),'west_market':(154,414),'east_market':(723,445),'west_south':(257,696),'east_south':(754,583),'south_avenue':(448,688),'south_gate':(448,735)}
checks={k:bool(a[int(y/896*150),int(x/896*150)]) for k,(x,y) in probes.items()}
mask=Image.fromarray(a.astype('uint8')*255); mask.save(OUT/'walkmask_150.png')
preview=Image.open(ROOT/'tianyong_city_master_preview_2048.png').convert('RGB')
layer=Image.new('RGB',preview.size,(42,238,108)); alpha=mask.resize(preview.size,Image.Resampling.NEAREST).point(lambda x: int(x*.36))
overlay=Image.composite(layer,preview,alpha); draw=ImageDraw.Draw(overlay)
for k,(x,y) in probes.items():
    x=x/896*2048;y=y/896*2048;draw.ellipse((x-8,y-8,x+8,y+8),fill='white',outline='red',width=3);draw.text((x+10,y),k,fill='red')
overlay.save(OUT/'walkmask_overlay_2048.png')
manifest={'coordinate_canvas':896,'master_size':6144,'resolution':150,'cell_world_size':2,'regions':regions,'obstacles':blocks,'probes':probes,'probe_checks':checks,'walkable_cells':int(a.sum()),'walkable_percent':round(float(a.mean()*100),2),'discarded_disconnected_cells':disconnected,'mask_sha256':hashlib.sha256(mask.tobytes()).hexdigest()}
(OUT/'navigation.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:manifest[k] for k in ['probe_checks','walkable_cells','walkable_percent','discarded_disconnected_cells']},ensure_ascii=False))
if not all(checks.values()): raise SystemExit('路径端点检查未通过，请审阅覆盖图')
packed=np.packbits(a.flatten(),bitorder='big').tobytes(); encoded=base64.b64encode(packed).decode()
cs=CLIENT/'Assets/Scripts/World/Tianyong/TianyongPaintedCity.cs'; text=cs.read_text(encoding='utf-8')
text=re.sub(r'private const string WalkMaskBase64 =\s*(?:"[A-Za-z0-9+/=]+"\s*\+?\s*)+;', 'private const string WalkMaskBase64 =\n'+ ' +\n'.join('            "'+encoded[i:i+100]+'"' for i in range(0,len(encoded),100))+';',text)
text=text.replace('MSB first). Generated from the master image by classifying beige\n        /// pavement pixels (low saturation, bright, warm), keeping cells with\n        /// ≥55 % pavement, clipping the outer city wall and despeckling twice.', 'MSB first). Festival artwork ground and obstacle polygons are traced in\n        /// image/tianyong_festival_hd_20260910/runtime/build_city_runtime.py.\n        /// Cells require 70% ground coverage and belong to the spawn component;\n        /// bridges and stairs remain connected, roofs/canals/props are blocked.')
cs.write_text(text,encoding='utf-8')
for r in range(1,7):
    for c in range(1,7):
        shutil.copy2(ROOT/f'Tiles/city_r{r:02}_c{c:02}.png',CLIENT/f'Assets/Resources/World/Tianyong/SceneTiles6x6/Tiles/tianyong_r{r:02}_c{c:02}.png')
art=CLIENT/'Assets/Art/World/Tianyong/SceneTiles6x6/Previews'
for f in ['tianyong_city_master_6144.png','tianyong_city_master_preview_2048.png']:shutil.copy2(ROOT/f,art/f)
shutil.copy2(OUT/'walkmask_overlay_2048.png',art/'tianyong_walkmask_overlay_2048.png')
shutil.copy2(ROOT.parent/'qdao_festival_scenes_20260910/runtime/01_main_city_wide_2560x1080.png',CLIENT/'Assets/Resources/World/Tianyong/Backgrounds/tianyong_city_main_64x27_v1.png')
print('36 tiles, two previews, fallback and client mask integrated')

