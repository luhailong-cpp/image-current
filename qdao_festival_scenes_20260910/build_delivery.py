from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
from datetime import datetime, timezone
import hashlib,json,shutil
root=Path(__file__).resolve().parent
items=[('01_main_city_wide','main_city_wide','主城横版'),('02_login_landscape','login_landscape','仙山登录背景'),('03_sanctuary_courtyard','main_city_wide','道观庭院背景'),('04_battle_forest_bridge','battle_forest_bridge','森林石桥战斗场景'),('05_battle_entry','battle_entry','战斗入场插画')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for _,scene,_ in items:
 p=root/scene/'scene-native.png'; q=root/scene/'scene.prompt.txt'
 if not p.is_file(): raise SystemExit(f'Missing generated scene: {p}')
 if not q.is_file() or len(q.read_text(encoding='utf-8-sig').strip())<200: raise SystemExit(f'Missing actual prompt: {q}')
final=root/'final'; final.mkdir(exist_ok=True)
records=[]
for name,scene,title in items:
 src=root/scene/'scene-native.png';dest=final/(name+'.png');shutil.copyfile(src,dest)
 with Image.open(dest) as im:
  im.load(); size=im.size; mode=im.mode
 assert sha(src)==sha(dest)
 records.append({'id':name,'title':title,'file':str(dest.relative_to(root)).replace('\\','/'),'sourceScene':scene,'nativeSource':scene+'/scene-native.png','nativeWidth':size[0],'nativeHeight':size[1],'outputWidth':size[0],'outputHeight':size[1],'mode':mode,'sha256':sha(dest),'resized':False,'prompt':scene+'/scene.prompt.txt','promptSha256':sha(root/scene/'scene.prompt.txt')})
manifest={'status':'art-assets-complete','completedAtUtc':datetime.now(timezone.utc).isoformat(),'generationTool':'built-in image_gen','modelIdentifierExposed':False,'qualityParameterExposed':False,'outputPolicy':'Preserve actual native outputs; no source-art upscaling. Native aspect ratios are recorded, not stretched to legacy pixel sizes.','runtimeIntegrated':False,'fiveUsesFourUniqueScenes':'main_city_wide and sanctuary_courtyard shared the same original source and share the same new painting.','outputs':records}
(root/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
unique=[records[0],records[1],records[3],records[4]]
card_w,card_h=896,384
sheet=Image.new('RGB',(card_w*2,card_h*2),(237,231,215))
font_path=Path(r'C:\Windows\Fonts\msyh.ttc')
font=ImageFont.truetype(str(font_path),22) if font_path.exists() else ImageFont.load_default()
for n,item in enumerate(unique):
 with Image.open(root/item['file']) as raw:
  thumb=ImageOps.contain(raw.convert('RGB'),(card_w-24,card_h-50),Image.Resampling.LANCZOS)
 x=(n%2)*card_w;y=(n//2)*card_h
 sheet.paste(thumb,(x+(card_w-thumb.width)//2,y+10))
 ImageDraw.Draw(sheet).text((x+18,y+card_h-32),item['title'],font=font,fill=(35,67,49))
sheet.save(root/'scene-review-contact.jpg',quality=92)
readme=['# Q版道家节庆场景 · 完成交付','', '已按用户提供的玉绿、暖金、象牙米白角色界面重绘，保留原场景主要构图、用途和活动空间，加入适量春节、元宵、中秋点缀。','', '| 用途 | 成图 | 原生尺寸 |','|---|---|---|']
for item in records:readme.append(f"| {item['title']} | [{item['id']}.png]({item['file']}) | {item['nativeWidth']}×{item['nativeHeight']} |")
readme+=['','主城横版与道观庭院原来共用一张底图，因此交付两个用途文件，图像相同。其余三类各自重绘。','', '成图按工具实际返回的原生像素保存，未插值放大；未强行拉伸到旧文件的2560×1080。若接入固定画布，需按页面的安全区域进行适配。','', '原图均保留，各场景子目录保存source-reference.png、scene-native.png和完整scene.prompt.txt。manifest.json记录尺寸、文件哈希和来源。scene-review-contact.jpg仅作缩小审阅。','', '本次为美术资源交付，尚未覆盖客户端资源或执行游戏内验收。主城6144高清地图另见[地图交付](../tianyong_festival_hd_20260910/README.md)。']
(root/'README.md').write_text('\n'.join(readme)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','uses':len(records),'uniqueGeneratedScenes':4,'allNativeFilesPreserved':True,'dimensions':[{'id':i['id'],'size':[i['nativeWidth'],i['nativeHeight']]} for i in records]},ensure_ascii=False))
