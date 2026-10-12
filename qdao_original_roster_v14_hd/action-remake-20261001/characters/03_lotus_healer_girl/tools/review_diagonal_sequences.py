from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime
B=Path(__file__).resolve().parents[1]; R=B/'review'; R.mkdir(exist_ok=True)
stamp=datetime.datetime.now().astimezone().isoformat()
choices={
'SE':['01-v1','02-v1','03-v1','04-v2','05-v1','06-v1','08-v1','07-v2','09-v1','10-v1','11-v2','12-v2','13-v1','14-v3','16-v1','16-v2'],
'SW':['01-v1','02-v1','03-v1','04-v2','05-v2','06-v1','07-v2','08-v1','09-v2','10-v1','11-v1','12-v2','13-v1','14-v3','15-v1','16-v1']}
phases={
'SE':[
'近右前脚足跟接触，远左腿后收；近右灯后、远左瓶前',
'近右前脚全掌承重、膝屈缓冲；远左腿后收',
'近右仍为前侧承重，远左后脚回收；中支撑推进不足',
'近右脚移至身体下方后段支撑，远左膝通过；灯到髋侧',
'近右后腿前掌蹬离姿，远左前膝屈曲；灯前瓶后',
'近右后膝收起、远左前膝回收；双足离地',
'远左前腿开始展开、近右腿后折；双足离地',
'远左前腿进一步伸向前下方，前跟下落；近右腿后折',
'远左前脚足跟接触姿，近右腿后收；近右灯前、远左瓶后',
'远左前脚全掌承重压缩，近右腿后收',
'远左脚移向身体下方承重、近右膝通过；手臂仍接近前后极值',
'远左后腿伸展支撑、近右前膝屈曲；灯转后、瓶转前',
'双膝已屈曲且鞋均高于接触姿，实际为早腾空，不能称为支撑蹬地',
'双足收起的腾空回收顶点，近右膝向前',
'近右前腿伸出下降、远左腿后折；尚未到01接触高度',
'近右前鞋继续下落、远左腿后折；接向01接触，仍有可见间隙'],
'SW':[
'近左前脚足跟接触、远右腿后收；近左瓶后、远右灯前',
'近左前脚全掌承重缓冲、远右腿后收',
'近左前脚继续承重，远右腿回收；中支撑推进不足',
'近左脚移至身体下方后段支撑，远右前膝通过；瓶前灯后',
'近左后腿前掌蹬离姿、远右前膝屈曲；瓶前灯后',
'近左后腿折叠，远右前腿离地展开；两足短暂离地',
'远右前膝回收较高、近左后腿折叠；两足腾空顶点',
'远右前小腿展开下降，近左后腿折叠；两足离地',
'远右前脚足跟接触姿，近左后腿折叠；瓶前灯后',
'远右前脚全掌承重压缩，近左后腿折叠',
'远右脚移到身体下方承重、近左膝通过；瓶回腰侧、灯已到前',
'远右后腿伸下支撑、近左前膝屈曲，前鞋回收',
'远右后脚前掌蹬地、近左前膝展开；瓶后灯前',
'双脚收起的短腾空回收，近左膝领先',
'近左前跟已下降到接触高度，远右腿后折；初接触姿',
'近左前脚接触滚动/加载，远右腿仍后折；回接01']
}
issues={
'SE':[
['首接触腿髋部被裙摆遮挡，左右腿全圈归属仍需动态复核'],
['实际前鞋底1211较01的1181低30px；未做程序贴地'],
['头脸向右漂，前支撑脚仍偏前，中支撑推进不足'],
['支撑底1153与邻帧差距较大；04→05灯从髋侧到前极值跨度大','躯干更正面，前景灯袖近远肩归属有歧义，尚未独立确认，不能仅凭道具不变断言解剖持手正确'],
['后前掌只可按透视蹬地姿读取；真实地面锁定未验收，灯接近右边缘'],
['两足离地可读；前脚展开幅度后续仍跳变，灯接近右边缘'],
['此槽采用08-v1；较06头位和灯体大小变化仍明显'],
['此槽采用07-v2；前鞋伸出较长、灯体大于07/09且距右边缘仅9px'],
['前鞋底1203低于01接触底22px，左右腿前后反相仍受裙摆遮挡'],
['前掌贴地姿可读，但膝压缩有限，头位有漂移'],
['裸膝已修为完整白裤；头顶19比相邻约60上移约40px；灯仍在前极值'],
['后腿支撑已真实修出；灯11→12跨度大，支撑底1209与前段注册不同'],
['实际已经双足离地，非计划最终蹬地；01同向肢体归属须整圈核查'],
['root局部修复瓶裁边后选用；前后脚回收重叠，动态遮挡待验收'],
['源16-v1映射此槽，近右前鞋最低约1156，灯瓶摆幅仍较大'],
['源16-v2映射此槽，前鞋最低约1159，距01接触仍约22px；首尾头部与手臂位置需实播']
],
'SW':[
['首接触腿髋部被裙摆遮挡，左右腿全圈归属仍需动态复核'],
['前鞋底1195较01的1171低24px；头部承重下降不明显'],
['中支撑推进不足，鞋底1204低于01；头发右边缘仅9px'],
['错手04-v1已拒；本帧正确近左瓶/远右灯，但双臂比03提前到反向极值，头向左上漂'],
['错手05-v1已拒；本帧正确肩袖，后鞋最低1169；灯右侧余量约20px'],
['前鞋最低1176，按同腿09接触1203判断约27px离地；灯距右边仅2px，需动态边缘检查'],
['源07-v2保留真实膝回收，鞋底1068，比08约高97px；短腾空观感仍需实播，右边缘仅4px'],
['前鞋最低1165，按09同腿接触约38px间隙；头较09上移约17px'],
['错手裁边09-v1已拒；本帧肩袖修正后正确，近左后腿与远右前腿髋部遮挡仍需全圈审'],
['前鞋最低1204，头脸较09又向左漂约70px，承重感弱'],
['灯已到前极值，10→11跳变大；全身更正面，边缘x10..1249较紧'],
['后支撑腿已实际伸下、前脚收起；底1201，12→13后脚移位仍大'],
['远右后脚仍有接触，实际是末段蹬地而非飞行；前鞋露底不等于外撇'],
['root修复发梢/衣带裁边；最低整体像素为灯流苏，不可当鞋底'],
['近左前跟实际到1170接触高度，不能记录为腾空；初接触时间提前到1050ms'],
['实际接触/滚动，不能记晚腾空；16→01瓶与灯臂摆幅、头部位置仍需实播']
]}
support={'SE':['right']*5+['none']*3+['left']*4+['none']*4,
'SW':['left']*5+['none']*3+['right']*5+['none','left','left']}
contact={'SE':['heel_contact','flat_compression','flat_support','late_support','forefoot_push_pose','short_flight','flight_extension','flight_descent','heel_contact','flat_compression','mid_support','rear_support','early_flight','flight_recovery','flight_descent','pre_contact'],
'SW':['heel_contact','flat_compression','flat_support','late_support','forefoot_push_pose','short_flight','flight_recovery','flight_descent','heel_contact','flat_compression','mid_support','rear_support','forefoot_push','flight_recovery','initial_contact','contact_roll']}
root={'SE':[730,1181],'SW':[610,1171]}
events={'SE':[(1,'right_heel_contact'),(2,'right_flat_load'),(5,'right_forefoot_push_pose'),(6,'right_foot_off'),(9,'left_heel_contact'),(10,'left_flat_load'),(12,'left_rear_support'),(13,'left_foot_off'),(17,'next_cycle_right_heel_contact')],
'SW':[(1,'left_heel_contact'),(2,'left_flat_load'),(5,'left_forefoot_push_pose'),(6,'left_foot_off'),(9,'right_heel_contact'),(10,'right_flat_load'),(13,'right_forefoot_push'),(14,'right_foot_off'),(15,'left_initial_contact'),(16,'left_contact_roll')]}
groupissues=[
'All native canvases kept unchanged; fixed root is a diagnostic baseline, not confirmed ground registration.',
'Perspective-depth support feet need not share one y line; contact events are static pose interpretations, pending actual playback.',
'Head/torso horizontal and vertical registration and rigid prop size are not fully stable.',
'Known wrong-hand and clothing-corrupted variants are excluded, but complete shoulder/hip occlusion continuity remains unaccepted.',
'No client playback test; native RGBA/source completeness does not imply dynamic acceptance.'
]
for dr in ['SE','SW']:
 G=B/'generation'/dr; frames=[]; thumbs=[]
 for i,n in enumerate(choices[dr]):
  path=G/(n+'.png'); im=Image.open(path)
  assert im.mode=='RGBA' and im.size==(1254,1254),(path,im.mode,im.size)
  alpha=im.getchannel('A'); assert alpha.getextrema()==(0,255)
  for suf in ['prompt.txt','job.json','receipt.json']: assert (G/(n+'.'+suf)).exists(),(n,suf)
  meta_path=G/(n+'.png.generation.json'); meta=json.loads(meta_path.read_text(encoding='utf-8-sig'))
  sha=hashlib.sha256(path.read_bytes()).hexdigest();assert meta['sha256']==sha
  bounds=list(alpha.point(lambda v:255 if v>8 else 0).getbbox())
  frame=dict(slot=i+1,source=str(path).replace('\\','/'),sourceSha256=sha,durationMs=75,startMs=i*75,observedPhase=phases[dr][i],observedSupportFoot=support[dr][i],contactType=contact[dr][i],isFlight=support[dr][i]=='none',issues=issues[dr][i],visualAccepted=False,nativeCanvas=list(im.size),alphaGt8Bounds=bounds,footAxisObservation='Same-direction hip/knee/ankle/shoe chain inspected; flight soles may be visible. No blanket toe-axis acceptance.')
  frames.append(frame)
  review=dict(schemaVersion=1,reviewedAt=stamp,status='selected_wip_pending_full_cycle_review',imageViewed=True,sourceSha256=sha,selectedSlot=i+1,observedPhase=frame['observedPhase'],observedSupportFoot=frame['observedSupportFoot'],contactType=frame['contactType'],isFlight=frame['isFlight'],issues=frame['issues'],nativeCanvas=[1254,1254],nativeRoot=root[dr],visualAccepted=False,clientTested=False,actualModel=None,actualQuality=None)
  (R/f'run-{dr}-{i+1:02d}-selected-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
  # Root owns14-16 source records; aggregate reviews above cover selection without racing its receipts.
  if int(n[:2])<14:
   (G/(n+'.review.json')).write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
   meta['status']=review['status'];meta['review']=review
   meta_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
  thumb=im.resize((256,256),Image.Resampling.LANCZOS)
  bg=Image.new('RGBA',(256,256),(235,231,225,255));bg.alpha_composite(thumb);thumbs.append(bg)
 assert len(set(f['sourceSha256'] for f in frames))==16
 seq=dict(schemaVersion=1,character='03_lotus_healer_girl',action='run',direction=dr,updatedAt=stamp,nativeRoot=root[dr],nativeCanvas=[1254,1254],canvas=[1254,1254],rootStatus='fixed provisional diagnostic anchor from01; no perframe transforms',visualAccepted=False,clientTested=False,durationMs=1200,timingBasis='User latest instruction: uniform75ms perframe, 16 frames=1200ms; no phase weighting.',frames=frames,contactEvents=[dict(slot=s,atMs=(s-1)*75,event=e,basis='actual selected pose, provisional static reading') for s,e in events[dr]],issues=groupissues)
 (R/f'run-{dr}-sequence-input.json').write_text(json.dumps(seq,ensure_ascii=False,indent=2),encoding='utf-8')
 sheet=Image.new('RGB',(1024,4*284),(235,231,225));draw=ImageDraw.Draw(sheet)
 for i,t in enumerate(thumbs):
  x=i%4*256;y=i//4*284;sheet.paste(t.convert('RGB'),(x,y))
  draw.text((x+8,y+257),f'{dr}{i+1:02d}  {choices[dr][i]}  75ms',fill=(45,40,40))
 sheet.save(R/f'run-{dr}-contact.jpg',quality=95)
 thumbs[0].save(R/f'run-{dr}-trial.apng',format='PNG',save_all=True,append_images=thumbs[1:],duration=[75]*16,loop=0,disposal=0,blend=0)
 print(dr,'selected',len(frames),'unique',len(set(x['sourceSha256'] for x in frames)),'duration',sum(x['durationMs'] for x in frames))
# Nonselected generated variants owned here retain honest rejection reasons.
rejected={
'SE':{'04-v1':['未形成腿通过，仍是前侧接触极近姿'],'07-v1':['前伸鞋底1212低于同腿09接触1203，不能作腾空'],'11-v1':['动作参考污染服装，出现裸膝，已局部恢复为11-v2'],'12-v1':['计划后支撑但两脚实际均离地，已修12-v2']},
'SW':{'04-v1':['近侧肩袖连灯，已知持物手交换，不选'],'05-v1':['近侧肩袖连灯，持物手错误，且右边缘紧'],'07-v1':['灯意外从后跳到前，后袖残留/手臂归属不清，不选'],'07-v3':['局部展开过多，前鞋最低1195近同腿接触1203，失去计划回收相位；保留07-v2'],'09-v1':['近侧肩袖连灯且右边裁灯/流苏，不选'],'12-v1':['后腿仍折起、前鞋最低，未形成所需后支撑']}
}
for dr,entries in rejected.items():
 for n,errs in entries.items():
  path=B/'generation'/dr/(n+'.png')
  if not path.exists():continue
  rv=dict(schemaVersion=1,reviewedAt=stamp,status='not_selected',imageViewed=True,sourceSha256=hashlib.sha256(path.read_bytes()).hexdigest(),visualAccepted=False,issues=errs,actualModel=None,actualQuality=None)
  (path.parent/(n+'.review.json')).write_text(json.dumps(rv,ensure_ascii=False,indent=2),encoding='utf-8')
  mp=path.with_name(path.name+'.generation.json'); m=json.loads(mp.read_text(encoding='utf-8-sig'));m['status']='not_selected';m['review']=rv;mp.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')

