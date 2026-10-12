from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy");R=B.parent/"09_bamboo_archer_girl"
versions=[1,1,1,2,2,1,3,3,4,1,2,1,1,1,1,3]
observed=[
("right_contact_candidate","right","右靴全底较低，远左靴后折露底；靴尖沿NE、握持正确。01→02承重变化较小。"),
("right_load_candidate","right","右靴保持低位、右膝略弯，左靴仍后折；无外撇硬错，缓冲幅度需实播看。"),
("right_mid_support_candidate","right","右靴支撑、右膝弯曲增加；左摆腿仍在后折阶段，过膝推进不强，03→04支撑轨迹需复核。"),
("right_late_push_candidate","right_forefoot_uncertain","v2已修04v1左腿后伸倒边：实际右腿长后伸、左腿上提，承接03→05同侧。右靴大部分底面可见，不能只凭提示认定前掌真实压地。"),
("right_departure_candidate","right_toe_or_airborne","近右腿后伸、左腿前抬，正常离地跖屈不可当脚掌外撇；靴最低点比01支撑低，地面投影尚未核准。"),
("airborne_scissor_candidate",None,"双靴高于邻近支撑带，近右靴在前、左靴后折露底；保留原图，06→07实际剪摆速度需75ms实播判断。"),
("left_descent_candidate",None,"v3实际左靴前移抬起、右靴收回露底，左膝比09更弯。与07v1/v2左腿一直后折不同，已建立换腿，但双底可见和06转折仍需动态审。"),
("left_precontact_candidate",None,"v3左靴前伸，鞋底由07的倾斜向09较平底转变，右靴后折；上半保持09来源布局。最低点与09接近，不声称已精确命中提示高度。"),
("left_contact_candidate","left","v4修正09v2支撑靴轴；实际左靴跟在后左、尖向前右，右靴后折，左手卷右手笔。未采09v3放大/贴边副作用。"),
("left_load_candidate","left","新10v1左靴全掌低位、左膝压缩，右膝收回；笔手在09→11之间下摆，卷手身份不变。"),
("left_late_support_candidate","left","11v2保留已修持手身份，左靴向前右、跟渐抬，右脚后折；11→12支撑脚横向跨度仍待真实地平面核准。"),
("left_push_candidate","left_forefoot_uncertain","新12v1左腿后伸、左踝跖屈、右腿屈膝，前脚掌向NE；握持/2墨灵正确。前掌真实承重和透视根点未正式通过。"),
("left_departure_candidate","left_toe_or_airborne","左后伸靴露底为正常蹬离候选，右腿回收；不因露底判外撇。裤裆附近白色/杂色边缘仍需清边。"),
("airborne_right_reach_candidate",None,"新14v1两腿离支撑带、左靴后折露底，右靴向前准备下降；上身持物正确。"),
("right_descent_candidate",None,"新15v1右靴接近支撑带，左靴后折；右靴尖向NE。15→16头部轮廓大小变化仍需正常节奏判断。"),
("right_precontact_candidate",None,"16v3已将v1/v2过大的头和低于01支撑的前靴改善；右靴仍高于01落地位，方向正确。头较15小，不能仅因换版声明相机比例完全稳定。")
]
frames=[]
for n,(v,obs) in enumerate(zip(versions,observed),1):
 p=B/"staging"/f"run-NE-{n:02d}-v{v}.png";im=Image.open(p);a=im.getchannel("A")
 frames.append(dict(n=n,slot=f"run-NE-{n:02d}",key=p.stem,file=p.as_posix(),selectedFile=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),nativeSize=list(im.size),mode=im.mode,alphaRange=list(a.getextrema()),actualObservedState=obs[0],support=obs[1],notes=obs[2],handIdentity="anatomical_right_brush_left_scroll",blueSpiritCount=2,formalPass=False,formalVisualPass=False,formalDynamicPass=False))
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
d=dict(character=B.name,direction="NE",updatedAt=now,status="complete_candidates_pending_normal_speed_and_edge_review",counts=dict(expectedSlots=16,availableSlots=16,currentPngsIncludingRevisions=len(list((B/"staging").glob("run-NE-*.png"))),passed=0,newImagesThisReference09Round=14),missingSlots=[],timing=dict(cycleMs=1200,uniformFrameMs=75,frameCount=16,source="latest_user_instruction",comparisonOnly=False,runtimeExportedHere=False),reference=dict(character="09_bamboo_archer_girl",userAcceptedActionAppearance=True,clientAcceptance=False,sourceTimingNotAdopted=True,principle="按实图脚支撑侧/膝踝相位匹配，17 NE01右支撑、NE09左支撑，和09同编号不是相同半周。",poseMappings={"17-04":"09-12","17-07":"09-15","17-08":"09-16","17-10":"09-02","17-12":"09-04","17-14":"09-06","17-15":"09-07","17-16":"09-08"}),selectedForSequenceReview=frames,frames=frames,actualConfirmedCorrections=["04左/右腿相位倒边改正为右腿后伸","07/08建立左脚前摆→落地过渡","09支撑靴尖朝向NE","新补10/12/14/15/16五个缺槽","16头/靴位置从明显放大低垂版改善"],remainingMostImportant=[dict(id="ground_projection",slots=[3,4,5,11,12],finding="03→04右支撑延伸及11→12左蹬离仍需地面投影与真实承重校验；未拿1155提示线冒充实地。"),dict(id="flight_transition",slots=[6,7,8],finding="06→07剪摆发生较快，07双靴底面可见；已改善缺失前摆，但自然度要在1200ms完整循环实播。"),dict(id="head_scale_transition",slots=[15,16,1],finding="16v3较15头轮廓缩小，01接缝也需观察；自然上下不自动失败，但相邻比例尚未证明稳定。")],edgeStatus="saturated_red_cyan_and_some_white_edge_pixels_remain",groundAndRoot=dict(requestedDiagnosticY=1155,actualRootConfirmed=None,actualGroundConfirmed=False,noGlobalTranslationOrPerFrameBBoxNormalizationApplied=True),rejectedAttempts=[dict(file="run-NE-09-v3.png",reason="头身放大且右穗贴边"),dict(file="run-NE-16-v1.png",reason="头放大且预触地靴低于01支撑线"),dict(file="run-NE-16-v2.png",reason="仍头放大/前靴低，未按提示实际达成"),dict(file="run-NE-07-v2.png",reason="实际仍旧左后折/右前伸，未补左前摆"),dict(file="run-NE-08-v2.png",reason="腿角色有改但头身放大/右穗贴边")],modelEvidence=dict(configuredTarget="gpt-image-2.5-sunburst",configuredQuality="max",actualModel=None,actualQuality=None,note="各图真实request/tool-result/generation.json独立保存，内置工具不披露selector或实际model/quality。"),diagnosticSheets=["review/run-NE-reference09-selected-contact.png"],formalClientAcceptance=False)
for oldname in ["review-run-NE.json","grounding-NE.json"]:
 p=B/oldname
 if p.exists():
  old=json.loads(p.read_text(encoding="utf-8-sig"));old["historicalStatus"]="superseded_by_current_reference09_review";old["supersededAt"]=now
  hist=B/"review"/(p.stem+"-pre-reference09-history.json")
  if not hist.exists():hist.write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding="utf-8")
(B/"review-run-NE.json").write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
(B/"grounding-NE.json").write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
(B/"review/review-run-NE-reference09-20261003.json").write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
c=Image.new("RGB",(960,1056),(218,218,218));draw=ImageDraw.Draw(c)
for j,row in enumerate(frames):
 x=j%4*240;y=j//4*264;draw.text((x+4,y+4),row["key"],fill=(0,0,0));im=Image.open(row["file"]).resize((240,240),Image.Resampling.LANCZOS);c.paste(im,(x,y+24),im)
c.save(B/"review/run-NE-reference09-selected-contact.png")
print(json.dumps(dict(counts=d["counts"],selected=[x["key"] for x in frames],allSquareRGBA=all(x["mode"]=="RGBA" and x["nativeSize"][0]==x["nativeSize"][1] and x["nativeSize"][0]>=1024 for x in frames)),ensure_ascii=False))

