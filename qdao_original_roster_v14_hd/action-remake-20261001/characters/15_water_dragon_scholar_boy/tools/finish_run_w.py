from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
from datetime import datetime,timezone
b=Path(__file__).resolve().parents[1]
keys=['01-v1','02-v1','03-v5','04-v3','04-v1','06-v1','07-v2','05-v1','09-v2','10-v3','11-v3','12-v1','13-v2','14-v2','15-v2','16-v3']
phases=['left_contact','left_compression','left_midstance','left_toeoff','early_flight_right_leading','first_apex','first_descent','pre_right_contact','right_contact','right_compression','right_midstance','right_toeoff','early_flight_left_leading','second_apex','second_descent','pre_left_contact']
notes=[
'近左前靴落地，远右腿后折；远右扇前、近左空手后。',
'近左膝压缩承重，近左空手仍后摆，远右手稳握扇。',
'近左靴髋下支撑，远右膝通过；v5扇回至腰前的摆臂中间位，近左手空闲。',
'近左后靴前掌蹬离，远右膝前屈；v2修后靴下指，v3内收远右持扇肘以衔接03，近左拳前、远右扇后。',
'原04v1实际早腾空，重选05而不重画；两脚离地、右腿前屈。',
'第一次腾空峰值，远右前腿和近左后腿分明，扇在后手。',
'v2修正下降期前脚高度，两脚仍离地，保持后扇。',
'原05v1实际接近右脚落地，重选08而不重画。',
'v2恢复远右前靴触地，近左脚后折，近左拳前远右扇后。',
'远右支撑屈膝承重，v3在v2正确后摆持手基础内收右肘，缓和接11时跨度，没有换手。',
'远右靴在髋下支撑、近左膝通过；v3只收回右扇至腰前，空左手回腰中间位。',
'远右后靴前掌蹬离，近左膝屈起领先，远右扇前摆。',
'v2保留第二早腾空两腿姿态并收住画布边缘扇面。',
'v2第二次腾空峰值，近左腿领先、右腿后折，扇前摆。',
'v2弯左膝抬靴，前靴约y1140，下降尚未触地，未抬整张图。',
'v3延伸近左小腿到预触地，保留前靴与地面间距；需在首尾连贯性中确认。']
frames=[];preview=[]
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
for i,key in enumerate(keys,1):
 p=b/'sources/new'/('run-W-'+key+'.png'); im=Image.open(p).convert('RGBA')
 sha=hashlib.sha256(p.read_bytes()).hexdigest(); rec='provenance/generation/run-W-'+key+'.json'
 assert im.size==(1254,1254) and (b/rec).exists()
 frames.append(dict(action='run',direction='W',frame=i,source=p.relative_to(b).as_posix(),sha256=sha,accepted=True,nativeSingleFrame=True,generationRecord=rec,review=dict(reviewer='finish_w',reviewedAt=datetime.now(timezone.utc).isoformat(),notes=notes[i-1]+' 静态候选；整体动态尚待主审。'),event=phases[i-1]))
 out=Image.new('RGBA',(1024,1024)); im.putalpha(im.getchannel('A').point(lambda a:0 if a<=8 else a));out.alpha_composite(im.resize((940,940),Image.Resampling.LANCZOS),(42,49))
 canvas=Image.new('RGB',(384,430),(226,230,234)); d=ImageDraw.Draw(canvas)
 d.text((8,6),f'W {i:02d} / '+key,font=font,fill=(20,50,65));small=out.resize((384,384),Image.Resampling.LANCZOS);canvas.paste(small,(0,36),small)
 for gy,col in [(942,(205,97,80)),(952,(120,146,170))]:d.line((0,36+gy*384/1024,384,36+gy*384/1024),fill=col,width=1)
 preview.append(canvas)
(b/'audit/run-W-selection.json').write_text(json.dumps({'frames':frames},ensure_ascii=False,indent=2),encoding='utf-8')
sheet=Image.new('RGB',(1536,1720),(226,230,234))
for i,im in enumerate(preview):sheet.paste(im,((i%4)*384,(i//4)*430))
sheet.save(b/'audit/run-W-selection-contact.png')
for name,total in [('legacy480',480),('trial640',640),('trial720',720),('trial800',800),('slow2880',2880)]:
 durations=[round((i+1)*total/160)*10-round(i*total/160)*10 for i in range(16)]
 preview[0].save(b/'audit'/f'run-W-{name}.gif',save_all=True,append_images=preview[1:],duration=durations,loop=0,disposal=2,optimize=False)
(b/'audit/run-W-preview-sources.json').write_text(json.dumps({'operation':'fixed1254to940inset42,49 then preview384; no pose transform', 'sourceFrames':frames,'trialCycleMs':[480,640,720,800],'adoption':'未定正式客户端时长，720仅试播'},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'selected':len(frames),'previews':6},ensure_ascii=False))


