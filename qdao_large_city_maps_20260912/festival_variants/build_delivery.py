from pathlib import Path

# This historical art packager must not overwrite the verified runtime delivery.
if (Path(__file__).resolve().parents[1] / 'runtime' / 'integration-delivery.json').exists():
    raise SystemExit('Integrated map delivery already exists. Historical art packaging stopped before writing files; see README.md and runtime/integration-delivery.json.')

from PIL import Image,ImageDraw,ImageFont
import hashlib,json
root=Path(r'E:\work\image\qdao_large_city_maps_20260912');out=root/'festival_variants';p=out/'penglai_mid_autumn';img=p/'map-native.png'
im=Image.open(img);im.load();size=list(im.size)
metadata={'name':'蓬莱岛·中秋月夜','generator':'built-in image_gen','image':'map-native.png','actual_native_size':size,'upscaled':False,'prompt':'map.prompt.txt','sha256':hashlib.sha256(img.read_bytes()).hexdigest(),'reference':'../../penglai_island/penglai-island-native.png','reference_transport':'工具本地路径通道ACL读取失败；使用刚显示的同一原图作为对话图片参考','generated_source':r'C:\Users\luyua\.codex\generated_images\01a08a28-6391-7100-a82e-f3a966e57349\exec-324d9c29-02b2-40b9-a889-7155cd47bb0c.png','status':'新增节庆美术图，尚未接入游戏'}
(p/'metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
im.thumbnail((896,896),Image.Resampling.LANCZOS);im.convert('RGB').save(p/'map-preview.jpg',quality=93)
review={'status':'passed','review':'已查看原生生成结果；完整岛屿与中央广场、道观、药圃、码头、南门及宽路保持，月夜明显且地面清晰。月兔、桂树、莲灯与船灯清楚，灰蓝屋瓦和自然木色保留。无人物文字UI；不做实际寻路验证声明。','checks':{'square_full_region':True,'bright_readable_night':True,'wide_roads_remain':True,'mid_autumn_mood':True,'native_no_upscale':True,'no_unified_jade_gold':True}}
(p/'visual-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
items=[('揽仙镇·春节','lanxian_spring_festival','红灯笼、红梅、迎春狮灯'),('东海渔村·元宵灯会','donghai_lantern_festival','鱼龙花灯、河灯、蓝调海港'),('蓬莱岛·中秋月夜','penglai_mid_autumn','月兔、桂树、银蓝月光')]
font=ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',25);small=ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',17)
thumb=560;gap=22;top=82;bottom=92;contact=Image.new('RGB',(thumb*3+gap*4,top+thumb+bottom),(243,239,231));d=ImageDraw.Draw(contact)
d.text((22,22),'新增三张节庆氛围大地图 · Q版道家',font=font,fill=(53,46,39))
records=[]
for i,(name,folder,note) in enumerate(items):
    f=out/folder/'map-native.png'; image=Image.open(f);image.load(); assert image.size==(1254,1254)
    prompt=out/folder/'map.prompt.txt';assert prompt.stat().st_size>100
    record={'name':name,'file':f'{folder}/map-native.png','size':list(image.size),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'prompt':f'{folder}/map.prompt.txt','native_no_upscale':True};records.append(record)
    x=gap+i*(thumb+gap);contact.paste(image.convert('RGB').resize((thumb,thumb),Image.Resampling.LANCZOS),(x,top));d.text((x,top+thumb+13),name,font=font,fill=(52,45,40));d.text((x,top+thumb+48),note,font=small,fill=(94,82,68))
contact.save(out/'festival-maps-preview.jpg',quality=94)
manifest={'request':'再多出几张蓬莱岛/东海渔村/揽仙镇完整Q版道家节庆大地图','count':3,'generated_with':'built-in image_gen','output_type':'完整区域氛围美术图','maps':records,'runtime_status':'未改游戏资源、导航或传送配置；原有日景地图均保留'}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
readme='''# 新增三张节庆氛围大地图

保留之前三张原创地图的完整区域、俯视比例、小建筑和宽路，再分别制作春节、元宵灯会和中秋月夜氛围。继续使用我们的Q版道家风格与各地自然配色，不强制青绿金。

![三张新增节庆大地图](festival-maps-preview.jpg)

| 地图 | 完整原图 | 氛围 |
|---|---|---|
'''
for name,folder,note in items:readme+=f'| {name} | [打开原图]({folder}/map-native.png) | {note} |\n'
readme+='''
三张均为内置image_gen返回的原生1254×1254，未放大。同目录保留手写提示词、来源元数据和视觉审查记录，manifest.json记录文件哈希。原来的三张日景地图保留，因此本轮三个地点共有6张正式大地图。

[回到原三张地图](../README.md) · [此前天墉城大地图索引](../catalog/已有大地图索引.md)

这些新增文件是地图美术图，还未建立新的游戏场景、寻路、碰撞或传送。未修改客户端、服务端或操作提交推送。
'''
(out/'README.md').write_text(readme,encoding='utf-8')
rootmanifest=root/'manifest.json';m=json.loads(rootmanifest.read_text(encoding='utf-8'));m['festival_variants']={'count':3,'manifest':'festival_variants/manifest.json','preview':'festival_variants/festival-maps-preview.jpg'};rootmanifest.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
p=root/'README.md';s=p.read_text(encoding='utf-8');link='> 已新增 [春节、元宵灯会、中秋月夜三张氛围大地图](festival_variants/README.md)，加上原三张，目前共6张正式地图。\n\n'
if link not in s:s=s.replace('\n\n','\n\n'+link,1)
s=s.replace('当前为三节元素综合版，未将它们冒充独立的三节夜景版本。','根目录的原三张为三节元素综合日景版；新增的独立节庆氛围版本见festival_variants。')
p.write_text(s,encoding='utf-8')
print(json.dumps({'new_maps':len(records),'total_current_locations':6,'all_native_1254':True,'preview':'festival_variants/festival-maps-preview.jpg'}))
