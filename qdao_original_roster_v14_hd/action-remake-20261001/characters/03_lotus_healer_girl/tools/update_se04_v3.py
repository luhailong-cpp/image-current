from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime
B=Path(__file__).resolve().parents[1];R=B/'review';G=B/'generation/SE'
stamp=datetime.datetime.now().astimezone().isoformat()
p=G/'04-v3.png';im=Image.open(p);sha=hashlib.sha256(p.read_bytes()).hexdigest()
assert im.mode=='RGBA' and im.size==(1254,1254)
bb=list(im.getchannel('A').point(lambda v:255 if v>8 else 0).getbbox())
issues=[
'近右支撑鞋实际约x545、底1209；比05的后足底1152低57px，地面锁定仍未整圈通过',
'远左摆动鞋最低约1138，回收高度低于请求，但与支撑鞋有明确高度差',
'头顶45比来源05的63上移18px，未作程序移动补偿；细微注册不作为本次拒绝理由',
'右灯手已收回至髋前，灯体仍偏前；03→04的前后摆切换仍有跨度，需全圈验收'
]
phase='近右脚回到身下后段支撑、膝稍屈且鞋尖沿SE；远左膝前驱脚折起；近右灯手从05前极值收回髋前，远左瓶仍在后'
review=dict(schemaVersion=1,reviewedAt=stamp,status='selected_wip_pending_full_cycle_review',imageViewed=True,sourceSha256=sha,selectedSlot=4,observedPhase=phase,observedSupportFoot='right',contactType='late_support',isFlight=False,visualAccepted=False,clientTested=False,issues=issues,nativeCanvas=[1254,1254],nativeRoot=[730,1181],alphaGt8Bounds=bb,actualModel=None,actualQuality=None,iterationCountThisTask=1,shoulderChainObservation='保留05-v1的近解剖RIGHT肩→前景大袖→莲灯链，far LEFT肩/袖在躯干后接玉瓶；比04-v2歧义明确改善',localResult='replace04-v2',comparisonMeasurements=dict(sourceHeadTopY=63,resultHeadTopY=45,sourceLowestRearShoeY=1152,resultSupportShoeY=1209,resultSwingShoeApproxY=1138,resultSupportShoeApproxX=545,resultRightWristApprox=[820,755],resultLanternCenterApprox=[1010,820]),measurementNote='alpha>8 bounds exact; individual joint/prop/foot centers are visual approximations on native canvas')
(G/'04-v3.review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'run-SE-04-selected-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
mp=G/'04-v3.png.generation.json';m=json.loads(mp.read_text(encoding='utf-8'));m['status']=review['status'];m['review']=review;mp.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
oldp=G/'04-v2.review.json';old=json.loads(oldp.read_text(encoding='utf-8'));old['status']='not_selected';old['supersededBy']='04-v3.png';old['issues'].append('已由正确05肩袖源生成04-v3替换，近远肩归属更可读');oldp.write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf-8')
omp=G/'04-v2.png.generation.json';om=json.loads(omp.read_text(encoding='utf-8'));om['status']='not_selected';om['review']=old;omp.write_text(json.dumps(om,ensure_ascii=False,indent=2),encoding='utf-8')
seqp=R/'run-SE-sequence-input.json';seq=json.loads(seqp.read_text(encoding='utf-8-sig'))
assert seq['frames'][10]['source'].endswith('/11-v3.png'),'Do not overwrite root11-v3'
before11=dict(seq['frames'][10])
f=seq['frames'][3];f.update(source=str(p).replace('\\','/'),sourceSha256=sha,observedPhase=phase,observedSupportFoot='right',contactType='late_support',isFlight=False,issues=issues,durationMs=75,startMs=225,alphaGt8Bounds=bb,visualAccepted=False)
seq['updatedAt']=stamp;seq['durationMs']=1200;seq['latestSE04Update']='04-v3 from correct05-v1 shoulder source; 1 targeted builtin call, one-sided support and correct arms improved; registration remains WIP'
assert seq['frames'][10]==before11
seqp.write_text(json.dumps(seq,ensure_ascii=False,indent=2),encoding='utf-8')
sheet=Image.new('RGB',(1024,1136),(235,231,225));draw=ImageDraw.Draw(sheet);anim=[]
for i,f in enumerate(seq['frames']):
 q=Image.open(f['source']).convert('RGBA').resize((256,256),Image.Resampling.LANCZOS);bg=Image.new('RGBA',(256,256),(235,231,225,255));bg.alpha_composite(q);anim.append(bg)
 x=i%4*256;y=i//4*284;sheet.paste(bg.convert('RGB'),(x,y));draw.text((x+8,y+257),f"SE{i+1:02d}  {Path(f['source']).stem}  75ms",fill=(45,40,40))
sheet.save(R/'run-SE-contact.jpg',quality=95)
anim[0].save(R/'run-SE-trial.apng',format='PNG',save_all=True,append_images=anim[1:],duration=[75]*16,loop=0,disposal=0,blend=0)
(R/'run-SE04-v3-result.md').write_text('# SE04 narrow repair\n\nSelected generation/SE/04-v3.png over04-v2 after one builtin edit. The correct05-v1 nearRIGHT shoulder-to-foreground lantern sleeve chain is preserved; farLEFT flask remains behind. Right supportshoe is actually under body; lantern wrist returns toward hip. Native1254RGBA, transparent, fullcanvas retained. Actual model/quality undisclosed.\n\nHeadtop45 versus source05 top63; supportshoe bottom1209 versus source05 rearfoot1152. Swing shoe bottom about1138. These registration/depth differences remain for fullcycle review, but no longer justify keeping04-v2 shoulder ambiguity. Lamp03→04 travel still large. No second attempt made.\n\nUpdated only SE04 frame in latest sequence-input, preserving root-selected11-v3 and all other frames; re-rendered SE contact/APNG at75ms. Overall visualAccepted remains false. No totalmanifest edits and no image deletions.\n',encoding='utf-8')
print(json.dumps(dict(selected='04-v3',sha256=sha,bounds=bb,preserved11=seq['frames'][10]['source'],totalMs=sum(f['durationMs'] for f in seq['frames'])),ensure_ascii=False))

