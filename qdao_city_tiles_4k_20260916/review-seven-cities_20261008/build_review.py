from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, hashlib, zipfile
from datetime import datetime,timezone
R=Path(__file__).resolve().parent;A=R.parent;S=A/'builtin_q64_all_city_references'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
names=[('tianyong_festival','01 主城节庆'),('lanxian_day','02 小镇日景'),('lanxian_spring','03 小镇春节'),('donghai_day','04 渔村日景'),('donghai_lantern','05 渔村元宵'),('penglai_day','06 仙岛日景'),('penglai_mid_autumn','07 仙岛中秋')]
entries=[]
for key,title in names:
 p=S/key/'map-native-layout-reference.png';record=S/key/'map.record.json';d=json.loads(record.read_text(encoding='utf-8-sig'))
 assert sha(p)==d['outputSha256']
 with Image.open(p) as im: size=list(im.size)
 entries.append({'id':key,'title':title,'path':str(p),'sha256':sha(p),'pixels':size,'role':'Existing full-city design reference; not completed64K delivery','record':str(record),'recordSha256':sha(record),'zipName':title.replace(' ','_')+'.png'})
cp=A/'builtin_q64_production/parallel_20261005/tianyong_festival/canonical-layout-preview-only.png'
comparison={'title':'01 对照：当前制作的结构底图','path':str(cp),'sha256':sha(cp),'role':'1600px reduced preview of current6144px structural master; not current64K finished image','zipName':'01_当前结构底图预览.png'}
slots=[entries[0],comparison,*entries[1:]]
font=lambda n,b=False:ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc' if b else 'C:/Windows/Fonts/msyh.ttc',n)
W=1744;tile=800;gap=32;left=40;top=156;row=898;H=top+4*row+38
board=Image.new('RGB',(W,H),'#edf1f4');draw=ImageDraw.Draw(board)
draw.text((left,30),'七套主城 · 整城方案筛选',font=font(42,True),fill='#163c37')
draw.text((left,91),'01–07 为已有整城方案；01 右侧附当前结构底图。高清整城仍未完成。',font=font(24),fill='#516567')
for i,e in enumerate(slots):
 col=i%2;r=i//2;x=left+col*(tile+gap+32);y=top+r*row
 draw.rounded_rectangle((x,y,x+tile+24,y+row-24),radius=14,fill='white',outline='#d6dfe3',width=2)
 draw.text((x+14,y+13),e['title'],font=font(28,True),fill='#183c37')
 with Image.open(e['path']) as im: pic=im.convert('RGB').resize((tile,tile),Image.Resampling.LANCZOS)
 board.paste(pic,(x+12,y+61))
 e['boardRectLTRB']=[x+12,y+61,x+12+tile,y+61+tile]
p=R/'seven-city-designs.jpg';board.save(p,quality=94,subsampling=0)
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'purpose':'User requested all city design images to decide which appearances to stop','newImageGenerationCalls':0,'sourceImagesModified':False,'artworkEditsPerformed':False,'operation':'Mechanical downsample/label/contact-sheet only; source PNGs bundled byte-identically','existingDesignReferences':entries,'additionalCurrentStructurePreview':comparison,'limitations':['Full-city references were generated on2026-09-17; historical model/quality evidence preserved, never relabeled asnew2.5 outputs.','Festival production follows correspondingday topology; festival references mainly show color and decorations.','Source reference names are legacy IDs, not approved in-game placenames.','No set has completed64K tiles or formal whole-city acceptance.'],'contactSheet':{'file':str(p),'sha256':sha(p),'pixels':[W,H]},'formalDelivery':False}
(R/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'seven-city-designs.jpg.generation.json').write_text(json.dumps({'operation':manifest['operation'],'newImageGenerationCalls':0,'file':str(p),'sha256':sha(p),'derivedFrom':[{'file':e['path'],'sha256':e['sha256'],'rect':e['boardRectLTRB']} for e in slots]},ensure_ascii=False,indent=2),encoding='utf-8')
intro='七套主城整城方案筛选\n\n01 主城节庆\n02 小镇日景\n03 小镇春节\n04 渔村日景\n05 渔村元宵\n06 仙岛日景\n07 仙岛中秋\n\n这些1254×1254 PNG是已有整城方案参考，不是已完成的65536×65536高清整城。用于决定保留哪些视觉方案。\n01另附当前结构底图的1600预览；它与早期Q版整城方案略有区别。节庆高清制作以日景几何为准。\n原始图片未重绘、未放大、未修改。历史模型和质量记录放在provenance目录；本次仅整理展示。\n请按编号说明保留/不做，也可指出只保留白天或夜景。\n'
(R/'说明.txt').write_text(intro,encoding='utf-8')
zp=R/'七套主城方案预览.zip'
with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_STORED) as z:
 for e in entries:
  z.write(e['path'],e['zipName']);z.write(e['record'],'provenance/'+e['id']+'.record.json')
 z.write(cp,comparison['zipName']);z.write(p,p.name);z.write(R/'manifest.json','provenance/review-manifest.json');z.write(R/'说明.txt','说明.txt')
with zipfile.ZipFile(zp) as z:
 for e in slots: assert hashlib.sha256(z.read(e['zipName'])).hexdigest()==e['sha256']
(R/'package-verification.json').write_text(json.dumps({'zip':str(zp),'sha256':sha(zp),'bytes':zp.stat().st_size,'sourcePNGsByteIdentical':True,'imageCountIncludingStructurePreview':8,'newGenerationCalls':0},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'contactSheet':str(p),'zip':str(zp),'zipBytes':zp.stat().st_size,'all8SourcesByteIdentical':True},ensure_ascii=True))
