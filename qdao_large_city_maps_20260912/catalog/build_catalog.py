from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime,timezone
import hashlib,json
OUT=Path(r'E:\work\image\qdao_large_city_maps_20260912\catalog')
ROOT=Path(r'E:\work\image')
def F(path,role):
 p=Path(path)
 if not p.is_absolute(): p=ROOT/p
 if not p.exists(): return None
 with Image.open(p) as im: size=im.size
 return {'path':str(p),'role':role,'width':size[0],'height':size[1],'bytes':p.stat().st_size,'modified_utc':datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
entries=[
 {'id':'tianyong-festival-native','title':'天墉城·节庆原生稿（本次指定）','location':'天墉城','date_basis':'目录20260910；mtime另列，不等同生成时间','festivals':['春节','元宵','中秋'],'festival_mode':'同图综合点缀；无独立节日变体证据','evidence':str(ROOT/'tianyong_festival_gptimage2_20260910/manifest.json'),'evidence_field':'userDirection','production_note':'原生1254×1254，无放大。','files':[
 F('tianyong_festival_gptimage2_20260910/tianyong-festival-main-city-native.png','native'),F(r'E:\work\output\imagegen\tianyong_festival_gptimage2_20260910\tianyong-festival-main-city-native.png','output_copy')]},
 {'id':'tianyong-jade-gold-native','title':'天墉城·玉绿暖金风格稿','location':'天墉城','date_basis':'目录20260910','festivals':['春节','元宵','中秋'],'festival_mode':'同图综合点缀；无独立节日变体证据','evidence':str(ROOT/'tianyong_festival_stylematch_20260910/manifest.json'),'evidence_field':'visualDirection','production_note':'原生1254×1254，无放大。','files':[
 F('tianyong_festival_stylematch_20260910/tianyong-jade-gold-main-city-native.png','native'),F('tianyong_festival_hd_20260910/layout-source-native.png','layout_copy'),F(r'E:\work\output\imagegen\tianyong_festival_stylematch_20260910\tianyong-jade-gold-main-city-native.png','output_copy')]},
 {'id':'tianyong-festival-hd','title':'天墉城·节庆高清整图','location':'天墉城','date_basis':'manifest assembledAtUtc=2026-09-11T15:04:53.305905-04:00','festivals':['春节','元宵','中秋'],'festival_mode':'继承玉绿暖金稿的三节综合点缀','evidence':str(ROOT/'tianyong_festival_hd_20260910/manifest.json'),'evidence_field':'sourceLayout.file / composition / finalArtUpscaled','production_note':'36块独立1254图块裁接成6144×6144，成图未上采样；不是单次6144原生出图。','files':[
 F('tianyong_festival_hd_20260910/tianyong_city_master_6144.png','assembled_master'),F('tianyong_festival_hd_20260910/tianyong_city_master_preview_2048.png','preview'),F(r'E:\work\mmorpg-client\Assets\Art\World\Tianyong\SceneTiles6x6\Previews\tianyong_city_master_6144.png','client_current_master_copy'),F(r'E:\work\mmorpg-client\Assets\Art\World\Tianyong\SceneTiles6x6\Previews\tianyong_city_master_preview_2048.png','client_current_preview_copy')]},
 {'id':'tianyong-original-6x6','title':'天墉城·早期6×6归档','location':'天墉城','date_basis':'README归档日期2026-09-08','festivals':[],'festival_mode':'现有提示词未指定春节/元宵/中秋，不据灯笼自行定节日','evidence':str(ROOT/'tianyong_city_6x6/PROMPTS.md'),'evidence_field':'母图 / 单图精修','production_note':'6144×6144客户端归档；来源1254×1254。尺寸不代表单次生成原生分辨率。','files':[
 F('tianyong_city_6x6/Previews/tianyong_city_master_6144.png','archived_master'),F('tianyong_city_6x6/Previews/tianyong_city_master_preview_2048.png','preview'),F('tianyong_city_6x6/Previews/tianyong_city_master_source_wide_1254.png','source_layout'),F(r'E:\work\mmorpg-client\Assets\Art\World\Tianyong\SceneTiles6x6\Previews\tianyong_city_master_source_wide_1254.png','client_source_copy')]},
 {'id':'tianyong-qstyle-3072','title':'天墉城·早期Q版3072重绘','location':'天墉城','date_basis':'目录20260908','festivals':[],'festival_mode':'现有元数据未指定独立春节/元宵/中秋主题','evidence':r'E:\work\output\imagegen\qdao_city_v2_20260908\manifest.json','evidence_field':'sourceLayout / masterSize / sourcePatches / note','production_note':'9块1254原生局部图拼接成3072×3072；保留完整城市布局。','files':[
 F(r'E:\work\output\imagegen\qdao_city_v2_20260908\qdao_city_qstyle_master_3072.png','assembled_master'),F(r'E:\work\output\imagegen\qdao_city_v2_20260908\qdao_city_preview_1536.png','preview'),F(r'E:\work\output\imagegen\qdao_city_v2_20260908\qdao_city_qstyle_layout_native_1254.png','source_layout')]}
]
for e in entries:
 e['files']=[f for f in e['files'] if f]
 p=next((f['path'] for f in e['files'] if f['role']=='preview'),e['files'][0]['path'])
 im=Image.open(p).convert('RGB');im.thumbnail((576,576));thumb=OUT/(e['id']+'-thumb.jpg');im.save(thumb,quality=92);e['thumbnail']=str(thumb)
index={'schema':'qdao.large_map_catalog.v1','created_utc':datetime.now(timezone.utc).isoformat(),'scope':'已存在的完整城镇俯视图；不含本轮20260912新图、横版UI/战斗背景、角色、切片、指南放大图与重复备份','searched_roots':[str(ROOT),r'E:\work\output\imagegen',r'E:\work\mmorpg-client\Assets\Art'],'history_check':'image仓库 git log --all 文件名只读查询，未见此前地点/节日独立版本命名','result':'核实5个既有天墉城地图版本；其中3个有综合春节/元宵/中秋装饰依据。未找到此前蓬莱岛/东海渔村/揽仙镇或分开的三节氛围大图文件证据；仅限上述本地范围。','versions':entries,'excluded_wide_examples':[{'path':str(ROOT/'qdao_main_city_chibi_v1.png'),'size':[1930,815]},{'path':str(ROOT/'qdao_gpt_image2_refresh_v7/scenes/main-city.raw.png'),'size':[1930,815]},{'path':str(ROOT/'qdao_chibi_game_pack_v4/main-city_2560x1080.png'),'size':[2560,1080]}]}
(OUT/'index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
font=ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',24);small=ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',19)
sheet=Image.new('RGB',(1800,1330),'#f3eedf');draw=ImageDraw.Draw(sheet)
for i,e in enumerate(entries):
 x=(i%3)*600;y=(i//3)*660
 im=Image.open(e['thumbnail']);sheet.paste(im,(x+(600-im.width)//2,y+8));draw.text((x+12,y+590),e['title'],fill='#173d33',font=font);f=e['files'][0];draw.text((x+12,y+624),f"{f['width']}×{f['height']}  |  {'三节综合点缀' if e['festivals'] else '节日未单独标注'}",fill='#685437',font=small)
x=1215;y=720
for line in ['已找回 5 个天墉城版本','首张即用户指定的全城构图','','相同图片的母图/预览/复制','与 36 张切片不重复计数','','未找到旧蓬莱、东海、揽仙','分开的三节氛围版本尚无证据']:
 draw.text((x,y),line,font=font,fill='#173d33');y+=45
sheet.save(OUT/'existing-large-maps-contact.jpg',quality=92)
lines=['# 既有完整大城地图索引','',index['result'],'','本索引只整理旧文件，未改动原图。表中是完整地图版本数量，不把预览、复制、切片或单纯放大布局指南重复计算。文件修改时间不代表实际生成时间；逐文件尺寸、字节数、SHA-256 与 UTC 修改时间见 [index.json](index.json)。','','![既有完整大城地图联系表](existing-large-maps-contact.jpg)','','| 地图版本 | 完整图尺寸 | 节日依据 | 原图 |','|---|---|---|---|']
for e in entries:
 f=e['files'][0];url=Path(f['path']).as_posix();lines.append(f"| {e['title']} | {f['width']}×{f['height']} | {'春节、元宵、中秋综合点缀' if e['festivals'] else '未单独标注'} | [打开](<{url}>) |")
lines+=['','## 尺寸与制作来源','']
for e in entries: lines.append(f"- **{e['title']}**：{e['production_note']} 依据：[原目录记录](<{Path(e['evidence']).as_posix()}>){' 的 '+e['evidence_field'] if e['evidence_field'] else ''}。")
lines+=['','## 检索范围与未发现项','','已查看 `E:/work/image`、`E:/work/output/imagegen`、客户端 `Assets/Art`，读取地图清单及曝光调整备份映射，并只读查询 image 仓库所有现存分支历史的图像文件名。这里只能说明这些本地目录与历史中目前能核实的内容。','','没有将横版主城/庭院背景、登录画面、战斗场景、人物、512/1024地图切片算成这种整城大地图。`qdao_large_city_maps_20260912` 中本轮新出的蓬莱岛、东海渔村、揽仙镇也不计为“以前已经生成”的旧图。','','三个节庆天墉版本包含同图综合点缀，现有记录不支持把它们重命名为分别的春节版、元宵版或中秋版。']
(OUT/'已有大地图索引.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Catalog complete:',OUT,'versions=',len(entries),'file records=',sum(len(e['files']) for e in entries))
