from pathlib import Path
from PIL import Image, ImageDraw
import hashlib,json,datetime
B=Path(__file__).resolve().parents[1]
G=B/'generation'/'W'; R=B/'review'; R.mkdir(exist_ok=True)
choices=['01-v1','02-v1','03-v1','04-v3','05-v1','06-v2','08-v5','07-v3','09-v2','10-v2','11-v2','12-v1','13-v1','14-v1','15-v1','16-v1']
phases=[
'近左前脚足跟接触，远右后脚折叠；瓶近后、灯远前',
'近左前脚全掌承重，膝屈；远右脚仍在后方',
'近左全掌承重继续向髋下移动；远右后脚回收幅度较小',
'近左支撑脚到身体下方、跟部略抬；远右膝通过，鞋仍折后',
'近左后侧前掌蹬地，远右前膝折叠；瓶前灯后',
'近左刚离地、脚跟后收；远右前膝回收；两足腾空',
'两足腾空，远右前膝仍屈曲，脚回收；较高脚隙的回收相位',
'远右前腿再伸准备下落，近左后脚折叠；两足仍离地',
'远右前脚足跟接触姿，近左后脚折叠；瓶前灯后',
'远右前脚全掌承重、膝压缩，近左脚在后回收',
'远右身体下方全掌支撑，近左膝向前通过，灯回髋侧；11-v2局部恢复灯体量',
'远右支撑腿扫向后，近左膝在前折叠；灯已经转至前方',
'远右后侧前掌蹬地，近左前腿准备展开',
'远右脚刚离地、近左前膝回收；后足仅极小地面间隙',
'近左前腿伸出、远右后脚折叠；两足离地',
'近左前跟下降至接触前，远右后脚折叠；回接01'
]
issues=[
['仅单帧基准获parent接受；完整循环仍未验收'],
['身体压缩主要在膝部，头高相对01变化很小'],
['头部未随承重降低；摆臂仍接近01前极值'],
['04→05灯体从前方到后方跨度大，缺更充分髋侧通过；保留正确持物手优先于错手04-v2'],
['相对01头眼明显向左漂约70px；手臂提前接近反向极值'],
['相对01头眼左漂约80px；第一段腾空手臂变化偏小'],
['实际抬脚大于指示，最低足隙约76px，属于膝回收而非计划晚腾空；头部仍左漂'],
['前鞋过度向左伸出，08→09接触间隙落差较大；头水平与垂直注册仍漂'],
['头眼仍较01左漂约80px；局部修正后接触底仍低于诊断地面约7px'],
['承重底低于诊断地面约21px；头仍左漂；不可用整图移位掩盖'],
['11-v2局部恢复灯体量，持手与双脚保持；右侧头发靠近边缘；头向左漂'],
['灯从11髋侧到12前方过渡偏大；支撑鞋稍朝下左，足轴需全圈核查'],
['前腿伸展较14提前，13→14有回收反转；后鞋前掌轴需独立确认'],
['后足仅约3px间隙，初腾空可信度弱；右侧发梢靠近画布边缘'],
['前伸幅度大于16，15→16回收跨度；头部未出现计划约18px上升'],
['16→01头顶仍有约12px变化；需按固定根点试播复核']
]
stamp=datetime.datetime.now().astimezone().isoformat()
items=[]
for i,n in enumerate(choices):
 p=G/(n+'.png'); im=Image.open(p); a=im.getchannel('A'); bb=a.point(lambda v:255 if v>8 else 0).getbbox()
 sha=hashlib.sha256(p.read_bytes()).hexdigest()
 item=dict(slot=i+1,source=str(p).replace('\\','/'),sourceSha256=sha,observedPhase=phases[i],issues=issues[i],durationMs=75,visualAccepted=False,nativeCanvas=list(im.size),alphaGt8Bounds=list(bb),diagnosticLowestShoeY=bb[3]-1,diagnosticFloorClearance=1179-(bb[3]-1),measurementNote='Lowest shoe visually identified as lowest occupied feature in selected image; alpha>8 bbox bottom is diagnostic, not ground alignment.')
 items.append(item)
 selectedReview=dict(schemaVersion=1,reviewedAt=stamp,status='selected_wip_pending_full_cycle_review',visualAccepted=False,sourceSha256=sha,selectedSlot=i+1,observedPhase=phases[i],issues=issues[i],imageViewed=True,nearFarArms='near anatomical LEFT flask, far anatomical RIGHT lantern; corrected shoulder sources retained, full-cycle acceptance pending',shoeAxis='WEST side-profile intent; no blanket direction acceptance',nativeCanvas=list(im.size),alphaGt8Bounds=list(bb),nativeRoot=[610,1179],rootStatus='provisional diagnostic only; no sprite transformation',actualModel=None,actualQuality=None)
 if n!='01-v1': (G/(n+'.review.json')).write_text(json.dumps(selectedReview,ensure_ascii=False,indent=2),encoding='utf-8')
 gp=G/(n+'.png.generation.json'); meta=json.loads(gp.read_text(encoding='utf-8')); meta['status']='selected_wip_pending_full_cycle_review';meta['review']=selectedReview;gp.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
rejected={
'04-v2':['近侧可见肩袖连接莲灯，已知持物手交换','灯体缩小；虽然经过髋侧但不选'],
'06-v1':['近侧肩袖连接后灯，持物手错误；被正确肩源06-v2取代'],
'07-v1':['近侧肩袖连接后灯，持物手错误'],
'07-v2':['肩袖已正确，但前鞋最低1189低于1179，不能作为飞行；局部修为07-v3'],
'08-v1':['近侧肩袖连接后灯；前鞋底1187低于诊断地面'],
'08-v2':['前腿离地改善但肩袖修正失败，近臂仍持灯'],
'08-v3':['正确肩袖，但前鞋最低1196，不能作为晚腾空'],
'09-v1':['正确反向摆臂，但前鞋最低1204且头左漂'],
'10-v1':['未保持09反向摆臂，莲灯错误恢复到前方']}
for n,errs in rejected.items():
 p=G/(n+'.png')
 if not p.exists():continue
 rv=dict(schemaVersion=1,status='not_selected',visualAccepted=False,imageViewed=True,reviewedAt=stamp,issues=errs,sourceSha256=hashlib.sha256(p.read_bytes()).hexdigest(),actualModel=None,actualQuality=None)
 (G/(n+'.review.json')).write_text(json.dumps(rv,ensure_ascii=False,indent=2),encoding='utf-8')
 gp=G/(n+'.png.generation.json');meta=json.loads(gp.read_text(encoding='utf-8'));meta['status']='not_selected';meta['review']=rv;gp.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
failed=G/'08-v4.job.json';j=json.loads(failed.read_text(encoding='utf-8'));j['status']='failed_no_image';j['error']='image generation failed: network error: error sending request';failed.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
(G/'08-v4.review.json').write_text(json.dumps(dict(status='failed_no_image',imageViewed=False,error=j['error'],actualModel=None,actualQuality=None),ensure_ascii=False,indent=2),encoding='utf-8')
seq=dict(schemaVersion=1,character='03_lotus_healer_girl',action='run',direction='W',createdAt=stamp,nativeRoot=[610,1179],nativeCanvas=[1254,1254],canvas=[1254,1254],rootStatus='provisional fixed diagnostic baseline from W01, not accepted or realigned',visualAccepted=False,clientTested=False,durationMs=1200,timingBasis='uniform75ms per frame,1200ms offline default',frames=items,issues=['Head/torso registration drifts strongly left during reversed arm half-cycle; no programmatic compensation used.','Contact shoe heights vary around provisional1179; technical files do not imply dynamic acceptance.','04→05 and11→12 arm travel jumps;11-v2 restores lamp dimensions while keeping original grip and feet.','07 source08-v5 and08 source07-v3 are deliberately mapped by actual knee recovery then extension; no repeated image.','All 16 sources unique independent built-in generations/AI edits, nativeRGBA; builtin actual model and quality undisclosed.'])
(R/'run-W-sequence-input.json').write_text(json.dumps(seq,ensure_ascii=False,indent=2),encoding='utf-8')
# Whole-canvas uniform reduction only; no bbox fit or per-frame registration.
sheet=Image.new('RGB',(1024,4*284),(235,231,225));d=ImageDraw.Draw(sheet)
anim=[]
for i,it in enumerate(items):
 im=Image.open(it['source']).convert('RGBA').resize((256,256),Image.Resampling.LANCZOS)
 x=(i%4)*256;y=(i//4)*284
 back=Image.new('RGBA',(256,256),(235,231,225,255));back.alpha_composite(im)
 sheet.paste(back.convert('RGB'),(x,y))
 d.text((x+8,y+258),f"{i+1:02d} {choices[i]} | y={it['diagnosticLowestShoeY']}",fill=(30,30,30))
 anim.append(back.convert('RGB'))
sheet.save(R/'run-W-contact.jpg',quality=94)
# GIF would quantize75ms to10ms granularity, so APNG keeps exact75ms.
anim[0].save(R/'run-W-trial.apng',save_all=True,append_images=anim[1:],duration=[75]*16,loop=0,format='PNG')
lines=['# W run 16 候选复核','', '视觉未验收；客户端未测。原生1254透明，固定诊断根点(610,1179)，不作逐帧移图或贴地。','', '|槽|唯一源|实际相位|最低鞋y|问题|','|---|---|---|---|---|']
for i,it in enumerate(items):lines.append(f"|{i+1:02d}|{choices[i]}|{it['observedPhase']}|{it['diagnosticLowestShoeY']}|{'；'.join(it['issues'])}|")
lines += ['', '08-v4 调用失败原文：image generation failed: network error: error sending request。无PNG，随后按parent授权用两图来源重试08-v5成功。','', '可保留：身份、长波浪发、左太阳穴莲饰、改后左右持物；两段膝回收与展开；16→01接触前后近似连续。主要遗留：反向摆臂半圈头部大幅左漂、04→05灯跨度、11-v2灯体量已局部恢复、接触足底高度分散。','', '每槽独立来源与hash见run-W-sequence-input.json；模型/质量actual均null。']
(R/'run-W-review.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps(dict(selection=str(R/'run-W-sequence-input.json'),contact=str(R/'run-W-contact.jpg'),uniqueHashes=len({i['sourceSha256'] for i in items}),frames=len(items),visualAccepted=False),ensure_ascii=False))

