from pathlib import Path

# This historical art packager must not overwrite the verified runtime delivery.
if (Path(__file__).resolve().parent / 'runtime' / 'integration-delivery.json').exists():
    raise SystemExit('Integrated map delivery already exists. Historical art packaging stopped before writing files; see README.md and runtime/integration-delivery.json.')

from PIL import Image, ImageDraw, ImageFont
import json,hashlib
root=Path(r'E:\work\image\qdao_large_city_maps_20260912')
items=[('蓬莱岛','penglai_island/penglai-island-native.png','灰蓝瓦 · 海岛仙山 · 道观与港湾'),('东海渔村','donghai_fishing_village/donghai-fishing-village-native.png','灰瓦木屋 · 渔市码头 · 盐田与船坞'),('揽仙镇','lanxian_town/lanxian-town-native.png','暖木灰瓦 · 溪谷街镇 · 多桥与宽路')]
thumb=560; gap=22; top=82; bottom=92
canvas=Image.new('RGB',(gap*4+thumb*3,top+thumb+bottom),(243,239,231));d=ImageDraw.Draw(canvas)
font=ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',25);small=ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',17)
d.text((22,22),'原创 Q 版道家大地图 · 蓬莱岛 / 东海渔村 / 揽仙镇',font=font,fill=(55,49,42))
records=[]
for i,(name,rel,note) in enumerate(items):
    p=root/rel;im=Image.open(p);im.load();assert im.size==(1254,1254)
    record={'name':name,'file':rel,'size':list(im.size),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'upscaled':False,'status':'原生大地图美术；尚未新增游戏场景'};records.append(record)
    x=gap+(thumb+gap)*i;canvas.paste(im.convert('RGB').resize((thumb,thumb),Image.Resampling.LANCZOS),(x,top));d.text((x,top+thumb+13),name,font=font,fill=(48,43,38));d.text((x,top+thumb+48),note,font=small,fill=(91,80,65))
canvas.save(root/'three-large-maps-preview.jpg',quality=94)
manifest={'request':'完整宏观俯视大地图，原创布局和地域配色，Q版道家、春节元宵中秋；取消统一青绿金色','generated_with':'built-in image_gen','source_reference':'style-reference.png','reference_role':'规模、俯视方式与建筑比例','maps':records,'old_assets_catalog':'catalog/已有大地图索引.md','runtime_status':'本轮三张仅完成地图美术，未添加游戏场景、传送、碰撞或导航'}
(root/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
readme='''# 原创Q版道家大地图 · 2026-09-12

按用户所附天墉城大图的完整地图规模、俯视角度与小建筑比例制作。最终遵循最新纠正：不以青绿金色统一全图，采用适合各地的灰蓝瓦、木色、石路和海岸自然色。地形、街区、建筑布置重新设计；未使用《问道》的截图、地图、贴图或标志作为绘画输入。

![三张完整地图预览](three-large-maps-preview.jpg)

| 地图 | 完整原图 | 原生像素 |
|---|---|---|
'''
for name,rel,note in items:readme+=f'| {name} | [{name}]({rel}) | 1254×1254 |\n'
readme+='''
三张均保留工具真实原生像素，与用户指定参考的1254×1254尺寸相同；没有插值放大为6144再标作高清。画面按完整可探索区域绘制，宽路连接多个街区，点缀春节红灯笼、元宵花灯和中秋桂树月兔。当前为三节元素综合版，未将它们冒充独立的三节夜景版本。

每张地图的目录内保存手写提示词、原始生成来源、实际尺寸和文件校验。揽仙镇的旧青绿金草稿放在draft-jade-gold，仅以lanxian-town-native.png作为最终版本。使用内置image_gen生成。

## 以前的大地图

[旧大地图索引](catalog/已有大地图索引.md) · [旧图对照预览](catalog/existing-large-maps-contact.jpg)

本地核实到5个以前的天墉城完整地图版本；有3个使用综合春节、元宵、中秋元素。检索范围内暂未找到旧蓬莱岛、东海渔村、揽仙镇，或分别按三个节日制作的氛围版本。没有重命名旧混合版以冒充这些版本。

## 游戏接入状态

这三张新地点目前完成地图美术与文件交付，尚未增加到游戏场景、传送、碰撞、导航。

用户转向本轮大地图制作前，旧天墉城与五张背景的客户端资源接入已保存：36块贴图、新寻路遮罩、灯柱前景、页面背景和战斗脚位。2026-09-12离线260个C#文件编译0错误；新的Unity实机验收、服务端导航烘焙及gate/scene重启尚未执行，当前运行中的客户端和服务端未被中断。新旧导航未完成同步前，不将其标为游戏接入完成。

此前主城美术已发布在image仓库分支art/festival-city-scenes-20260912，提交0aaed0685ae9e9362e72ae87e20726a7f35b723e；本轮三张新地点尚未提交或推送。
'''
(root/'README.md').write_text(readme,encoding='utf-8')
p=Path(r'E:\work\image\SCENE_DELIVERY.md');s=p.read_text(encoding='utf-8')
lead='> 2026-09-12 新增：[蓬莱岛、东海渔村、揽仙镇完整大地图](qdao_large_city_maps_20260912/README.md)。已按最新要求取消统一青绿金配色，另整理[此前5个大地图版本](qdao_large_city_maps_20260912/catalog/已有大地图索引.md)。\n\n'
s=s.replace('本次已完成高清主城地图',lead+'2026-09-10批次已完成高清主城地图',1)
s=s.replace('本次完成的是美术资源。尚未覆盖客户端生产资源、更新主城寻路/碰撞/遮挡或执行游戏内验证。接入新主城时须同步客户端与服务端导航，并根据页面安全区域适配横版背景。当前图中的开阔地面不是已经验证的导航数据。','旧批次美术已发布到art/festival-city-scenes-20260912分支（0aaed0685ae9e9362e72ae87e20726a7f35b723e）。客户端生产贴图、导航遮罩、前景和背景已在本地接入并通过离线C#编译；Unity实机验证、服务端导航同步及进程重启尚未完成。用户随后转向新增三张完整大地图的制作，运行中的游戏未被中断。')
p.write_text(s,encoding='utf-8')
print(json.dumps({'maps_verified':len(records),'all_native_1254':True,'preview':'three-large-maps-preview.jpg','documentation_updated':True}))
