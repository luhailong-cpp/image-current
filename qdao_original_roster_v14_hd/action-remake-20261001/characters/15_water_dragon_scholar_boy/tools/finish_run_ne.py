from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageSequence
import json,hashlib
from datetime import datetime,timezone
b=Path(__file__).resolve().parents[1]
keys=['01-v4','02-v1','03-v1','04-v4','06-v1','05-v2','07-v1','08-v1','09-v1','10-v2','11-v2','12-v3','13-v2','14-v2','16-v1','15-v1']
phases=['左触地','左压缩','左中支撑','左蹬地','右领先早腾空','首腾空峰值','右下降','右近接触','右触地','右压缩','右中支撑','右蹬地','左领先早腾空','次腾空峰值','左下降','左近接触']
events=['left_contact','left_compression','left_midstance','left_toeoff','early_flight_right_leading','first_apex','first_descent','pre_right_contact','right_contact','right_compression','right_midstance','right_toeoff','early_flight_left_leading','second_apex','second_descent','pre_left_contact']
notes=['沿用root的01v4，左脚支持/右脚后折。','左膝屈曲承重；先审本次已生成稿。','左脚髋下，右脚通过，双手腰部中间位。','v1/v2换扇到左手已拒；v3从03单改左踝；v4补空左拳前摆中间位，右手仍握扇。','原06v1重选05，左后靴仍低、右前靴屈起，适合离地早期。','原05v2重选06，两靴均较高；避免原06后靴过低当峰值。','右靴已接近右侧地面投影，应在动态中确认触地开始。','右靴接地高度附近，不能简单当成完全悬空。','沿用root的09v1，右脚支持/左脚后折。','v1支撑靴过低拒选；v2保留09的靴位压髋屈膝，鞋底高度改善。','v1错误左支撑已拒，v2恢复右支撑，手臂回腰。','v1/v2错误左腿蹬地已拒；v3单修正确右脚踝的前掌蹬离。','v1腿反且扇超边已拒，v2保留左领先/右后折，双脚低空。','v2针对性抬左靴，实际高度变化小于提示目标，按实图低跳峰值评估。','原16v1重选15，鞋底略高于原15v1，左踝背屈。','原15v1重选16，左靴继续下降，衔接01；保留原图来源。']
frames=[];ims=[]
for i,key in enumerate(keys,1):
 p=b/'sources/new'/('run-NE-'+key+'.png'); im=Image.open(p).convert('RGBA');assert im.size==(1254,1254)
 rec='provenance/generation/run-NE-'+key+'.json';assert (b/rec).exists()
 aa=im.getchannel('A'); bb=aa.point(lambda a:255 if a>128 else 0).getbbox()
 # Manual shoe-region ROI: both boots below waist, no trailing fan tassel beyond x950.
 roi=aa.crop((350,1020,900,1254)).point(lambda a:255 if a>128 else 0).getbbox()
 sole=1020+roi[3]-1 if roi else None
 row=dict(action='run',direction='NE',frame=i,source=p.relative_to(b).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),generationRecord=rec,nativeSingleFrame=True,accepted=True,event=events[i-1],phaseObserved=phases[i-1],review=dict(reviewer='finish_w',reviewedAt=datetime.now(timezone.utc).isoformat(),notes=notes[i-1]+' 静态候选；动态整体仍待主审。'),nativeAlphaBBox=bb,shoeRegionBottomNative=sole,shoeRegionBottomExport=round(49+sole*940/1254,2))
 frames.append(row)
 out=Image.new('RGBA',(1024,1024));out.alpha_composite(im.resize((940,940),Image.Resampling.LANCZOS),(42,49));ims.append(out)
data=dict(frames=frames,selectionStatus='complete_16_candidates_not_final_dynamic_acceptance',clientStatus='not_integrated',fixedTransform={'native':1254,'resize':940,'inset':[42,49],'canvas':1024},actualModel=None,actualQuality=None)
(b/'audit/run-NE-selection.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
tiles=[]
for i,im in enumerate(ims):
 tile=Image.new('RGB',(384,430),(226,230,234)); sm=im.resize((384,384),Image.Resampling.LANCZOS);tile.paste(sm,(0,36),sm);d=ImageDraw.Draw(tile)
 d.text((6,5),f"NE{i+1:02d} {phases[i]} / {keys[i]}",font=font,fill=(23,45,58))
 # NE near left and far right support projections diagnosed separately.
 for native,col in [(1200,(185,75,69)),(1150,(86,140,160))]:
  gy=36+(49+native*940/1254)*384/1024;d.line((0,gy,384,gy),fill=col,width=1)
 tiles.append(tile)
sheet=Image.new('RGB',(1536,1720));[sheet.paste(im,((i%4)*384,(i//4)*430)) for i,im in enumerate(tiles)]
sheet.save(b/'audit/run-NE-selection-contact.png')
# Longer contact/compression, short low flight; tentative offline durations.
custom=[55,65,60,45,30,25,35,45,55,65,60,45,30,25,35,45]
assert sum(custom)==720
presets=[('legacy480',[30]*16),('trial640',[40]*16),('trial720',[45]*16),('trial800',[50]*16),('weighted720',custom),('slow2880',[180]*16)]
outs=[]
for sz in [240,384]:
 fs=[]
 for i,im in enumerate(ims):
  sm=im.resize((sz,sz),Image.Resampling.LANCZOS);tile=Image.new('RGB',(sz,sz+28),(221,229,236));tile.paste(sm,(0,28),sm);d=ImageDraw.Draw(tile);d.text((5,4),f'NE{i+1:02d} {phases[i]}',font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',12),fill=(23,45,58));fs.append(tile)
 for key,ds in presets:
  ends=[];t=0
  for dt in ds:t+=dt;ends.append(round(t/10)*10)
  actual=[v-(ends[j-1]if j else 0)for j,v in enumerate(ends)]
  p=b/'audit'/f'run-NE-{key}-{sz}.gif';fs[0].save(p,save_all=True,append_images=fs[1:],duration=actual,loop=0,disposal=2,optimize=False)
  chk=Image.open(p);dur=[x.info['duration']for x in ImageSequence.Iterator(chk)];assert len(dur)==16 and sum(dur)==sum(ds)
  outs.append(dict(file=p.relative_to(b).as_posix(),size=sz,frames=16,cycleMs=sum(ds),durationsMs=actual))
review=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),status='static_review_complete_browser_pending',frames=frames,rejected=['04-v1','04-v2','05-v1','11-v1','12-v1','12-v2','13-v1'],reselected={'05':'06-v1','06':'05-v2','15':'16-v1','16':'15-v1'},customDurationsMs=custom,timingComment='720ms仅离线接地试验；接触/承重停留较长，短腾空。非客户端正式时长。',exports=outs,clientStatus='not_integrated')
(b/'audit/run-NE-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'frames':16,'previews':len(outs),'feet':[r['shoeRegionBottomNative'] for r in frames]},ensure_ascii=False))

