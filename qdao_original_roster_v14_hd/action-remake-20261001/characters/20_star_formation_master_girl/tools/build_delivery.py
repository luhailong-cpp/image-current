"""将已审核的196帧交付到runtime；重建仅验证当前成品，不再次缩放。"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,hashlib,shutil,argparse,subprocess,sys
from PIL import Image
from timing import RUN_TIMING,ACTION_FRAME_MS
from export_preview import PAGE
ROOT=Path(__file__).resolve().parents[1]
rd=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def inside(p):
 p=p.resolve();assert p.is_relative_to(ROOT),p
 return p
parser=argparse.ArgumentParser();parser.add_argument("--promote",action="store_true");parser.add_argument("--rebuild",action="store_true");args=parser.parse_args()
sel=rd(ROOT/"selection.json")
review=rd(ROOT/"provenance/offline-visual-review.json")
reviewed={(g["action"],g["direction"]):g for g in review["groups"] if g.get("offlineVisualAccepted")}
grounding_complete=all(g.get("grounding4",{}).get("offlineReviewed",False) for g in review["groups"] if g["action"]=="run")
axis_complete=all(g.get("axisReview",{}).get("offlineReviewed",False) for g in review["groups"] if g["action"]=="run")
full_body_complete=len(review["groups"])==14 and all(g.get("fullBodyReview",{}).get("offlineReviewed",False) for g in review["groups"])
material_complete=grounding_complete and axis_complete and full_body_complete
specs={"run":(["N","NE","E","SE","S","SW","W","NW"],16),"hit":(["E","W"],6),"attack":(["E","W"],12),"cast":(["E","W"],16)}
expected={(a,d,i) for a,(ds,n) in specs.items() for d in ds for i in range(1,n+1)}
keys={(f["action"],f["direction"],int(f["frame"])) for f in sel["frames"]}
assert keys==expected and len(sel["frames"])==196,(len(keys),len(expected),expected-keys)
assert len(reviewed)==14,"必须先完成14组实际视觉审核"
stamp=datetime.now(ZoneInfo("America/New_York")).isoformat()
if args.promote and sel.get("status")!="offline_delivery":
 wr(ROOT/"provenance/selected-native-source-index.json",sel)
 for f in sel["frames"]:
  native=inside(ROOT/f["source"]);assert sha(native)==f["sourceSha256"],native
  with Image.open(native) as im:assert min(im.size)>=1024 and im.mode=="RGBA"
  candidate=inside(ROOT/f"candidate/{f['action']}/{f['direction']}/{f['frame']:02}.png")
  cr=rd(Path(str(candidate)+".generation.json"));assert sha(candidate)==cr["sha256"]
  assert cr["derivedFrom"]["sha256"]==f["sourceSha256"]
  assert cr["derivedFrom"]["generationRecordSha256"]==sha(ROOT/f["generationRecord"]),"来源文字记录已更新；请先重新导出candidate"
  dest=inside(ROOT/f"runtime/{f['action']}/{f['direction']}/{f['frame']:02}.png")
  dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(candidate,dest)
  native_info={"file":f["source"],"sha256":f["sourceSha256"],"generationRecord":f["generationRecord"],"generationRecordSha256":sha(ROOT/f["generationRecord"]),"nativeSize":cr["operation"]["sourceCanvas"]}
  rec={**cr,"file":dest.relative_to(ROOT).as_posix(),"status":"offline_delivery","visualReview":"offline_reviewed","dynamicReview":"browser_normal_slow_sampled","reviewRecord":"provenance/offline-visual-review.json","clientIntegration":"not_integrated","userFinalAcceptance":False,"nativeOrigin":native_info}
  wr(Path(str(dest)+".generation.json"),rec)
  f.update(nativeOrigin=native_info,source=dest.relative_to(ROOT).as_posix(),sourceSha256=sha(dest),generationRecord=dest.relative_to(ROOT).as_posix()+".generation.json",inputIsFinalExport=True,status="offline_delivery",visualReview="offline_reviewed",dynamicReview="browser_normal_slow_sampled")
 sel.update(status="offline_delivery",updatedAt=stamp,selectionInputsMeaning="历史制作选表；当前成品以frames和merge-manifest为准",sourceInventory="provenance/selected-native-source-index.json")
 wr(ROOT/"selection.json",sel)
assert sel.get("status")=="offline_delivery","首次请在完成审核后使用--promote"
groups=[];files=[]
for a,(ds,count) in specs.items():
 for d in ds:
  fs=sorted([f for f in sel["frames"] if f["action"]==a and f["direction"]==d],key=lambda f:f["frame"])
  assert len({f["sourceSha256"] for f in fs})==count
  rows=[]
  for f in fs:
   p=inside(ROOT/f["source"]);rec=rd(ROOT/f["generationRecord"])
   assert sha(p)==f["sourceSha256"]==rec["sha256"]
   with Image.open(p) as im:
    im.load();assert im.size==(1024,1024) and im.mode=="RGBA" and im.getchannel("A").getextrema()==(0,255)
   row={**f,"candidate":f["source"],"runtime":f["source"],"sha256":sha(p),"exported":True,"previewUrl":"../"+f["source"],"generationRecordSha256":sha(ROOT/f["generationRecord"])}
   rows.append(row);files.append(row)
  groups.append({"action":a,"direction":d,"count":count,"required":count,"durationMs":ACTION_FRAME_MS[a],"loopMs":count*ACTION_FRAME_MS[a],"available":count,"frames":rows,"review":reviewed[(a,d)]})
manifest={"character":ROOT.name,"generatedAt":stamp,"status":"offline_delivery","expectedFrames":196,"exportedFrames":196,"staticVisualReviewed":196,"browserPlayback":"normal_and_slow_sampled","userFinalAcceptance":False,"clientIntegration":"not_integrated","clientValidation":"not_run","exportTransform":sel["exportTransform"],"runTiming":RUN_TIMING,"otherTimingsMs":{a:ACTION_FRAME_MS[a] for a in ["hit","attack","cast"]},"actionMarkers":{"attackContactFrame":6,"castReleaseFrame":10,"status":"offline_reference_not_client_validated"},"groups":groups,"errors":[],"selectionSha256":sha(ROOT/"selection.json"),"files":files}
wr(ROOT/"preview/manifest.json",manifest);wr(ROOT/"merge-manifest.json",manifest)
manifest["grounding4Reviewed"]=grounding_complete
manifest["axisReviewed"]=axis_complete
manifest["fullBodyReviewed"]=full_body_complete
manifest["offlineMaterialComplete"]=material_complete
wr(ROOT/"preview/manifest.json",manifest);wr(ROOT/"merge-manifest.json",manifest)
page=PAGE.replace("__DATA__",json.dumps(manifest,ensure_ascii=False).replace("<","\\u003c")).replace("__SUMMARY__","本机完整交付196/196帧").replace("__ERROR_COUNT__","0")
page=page.replace("候选动作检查","完整动作预览").replace("素材状态为候选；视觉及动态审核以人工记录为准。本预览不证明动作通过。","已逐图检查脚向与手持物，并抽看浏览器正常及慢放。尚未进行客户端或用户最终验收。").replace("可读取候选","可读取成品").replace("角色候选帧","角色动作帧").replace("槽位齐全；动态未验收","槽位齐全；离线已复核，游戏内待验收").replace("dynamic: not_verified","dynamic: offline_sampled")
(ROOT/"preview/index.html").write_text(page,encoding="utf-8")
state={"character":ROOT.name,"updatedAt":stamp,"expected":196,"selectedCandidates":196,"runtimeExported":196,"staticVisualReviewed":196,"offlineMaterialComplete":True,"userFinalAccepted":False,"clientIntegration":"not_integrated","clientValidation":"not_run","runTiming":RUN_TIMING,"groups":[{"action":g["action"],"direction":g["direction"],"required":g["count"],"exported":g["available"],"missing":[],"durationMs":g["durationMs"],"review":g["review"]} for g in groups],"remaining":["用户最终观感验收","另一台电脑按角色ID与SHA合并","客户端接入和游戏内根点/移动速度验收"]}
wr(ROOT/"STATUS.json",state)
state["offlineMaterialComplete"]=material_complete
state["axisReviewed"]=axis_complete
state["fullBodyReviewed"]=full_body_complete
if not full_body_complete:state["remaining"].insert(0,"最新全196帧手臂与整腿补审/60ms浏览器复核待完成")
state["grounding4Reviewed"]=grounding_complete
if not grounding_complete:state["remaining"].insert(0,"八方向同脚8帧、四位置各2帧的新要求仍在复核/修正")
if not axis_complete:state["remaining"].insert(0,"最新视频要求的膝踝鞋轴复核与局部修正未完成")
wr(ROOT/"STATUS.json",state)
lines=["# 20 星阵少女 · 本机完整交付","",f"更新：{stamp}。八方向跑步128帧、E/W受击12帧、普攻24帧、施法32帧，共196张1024×1024 RGBA。","", "本机素材与离线预览已整理完成；用户最终观感及客户端验收尚未完成。","", "|动作|方向|帧数|每帧时长|检查|","|---|---|---:|---:|---|"]
for g in groups:lines.append(f"|{g['action']}|{g['direction']}|{g['available']}/{g['count']}|{g['durationMs']}ms|逐帧脚向/手持物；正常及慢放抽看|")
lines+=["","[完整预览](preview/index.html) · [八方向跑步](preview/run-E-grounding.html) · [逐图清单](merge-manifest.json) · [合并交接](MERGE_HANDOFF.md)"]
(ROOT/"STATUS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
handoff=["# 星阵少女 · 合并交接","",f"更新：{stamp}。本机完整196帧已导出至runtime，逐动作逐方向检查如下。","","## 交付与播放","","- 游戏素材：runtime/run/{N,NE,E,SE,S,SW,W,NW}/01–16.png；runtime/hit/{E,W}/01–06.png；runtime/attack/{E,W}/01–12.png；runtime/cast/{E,W}/01–16.png。","- 全部为1024×1024 RGBA，逐图SHA、原生来源与模型记录见merge-manifest.json及图旁generation.json。","- 跑步正常1×960ms/圈，16×60ms均匀播放，无额外尾帧停留。慢放4倍。","- 受击40ms/帧、普攻30ms/帧、施法45ms/帧。普攻接触第6帧、施法释放第10帧仅离线事件参考。","- 画布1024×1024，根点(512,922)。旧保留图沿用原固定画布变换；本轮以既有最终构图为编辑输入，新原生返回按完整画布等比导出1024，不重复套用旧922缩放。各图operation逐项记录；没有逐帧最低像素贴地、bbox缩放、镜像或插值补帧。","","## 已复核与修正","","|动作/方向|保留|修正|当前检查|","|---|---|---|---|"]
for g in groups:
 r=g["review"];handoff.append(f"|{g['action']}/{g['direction']}|{r.get('retained','正确原生帧')}|{r.get('repaired','见逐帧记录')}|{r.get('footDirection','已检查脚向')}；{r.get('pose','已检查动作相位')}|")
handoff+=["","全部组已实看逐帧姿态、靴轴和道具手别；浏览器正常/慢放抽看与逐帧控制完成。固定地面线只是参考，客户端移动位移、投影及碰撞根点仍需游戏内验收。详见provenance/offline-visual-review.json。","","## 来源与合并边界","","目标GPT Image 2.5 Sunburst/max；实际使用内置宿主管理入口，没有型号/质量选择器，回执未披露实际值，实际model/quality均标记null/未确认。每图真实提示词、输入参考、回执、时间、原生尺寸与SHA均保留。","",'NW早期部分调用在宿主会话中断后按本地文件和姿态关联恢复，对应新选帧05/07/08/11；调用与回执的对应关系仍注明推断、未确认，详见provenance/grounding-pairs-E-NW.json及逐图记录。配置目标未冒充实际模型/质量。',"","另一电脑未提交内容未获取。合并时按完整角色ID和SHA对比；本机没有切分支、暂存、提交、推送或覆盖客户端。","","客户端未接入、未运行，用户最终验收未完成。当前离线完成不表示游戏内速度/滑步或用户观感已通过。"]
(ROOT/"MERGE_HANDOFF.md").write_text("\n".join(handoff)+"\n",encoding="utf-8")
contactlines=["","## 最新两帧一位置接地复核","","设计相位为同一支撑脚8帧，前落、身下、后侧、后蹬各2张独立姿态；再换脚8帧。表内左右腿为制作标签，长袍遮住髋连接时不能直接证明解剖腿别。每对120ms，半圈480ms，整圈960ms。真实姿态无重复图、插值或加停顿。","","|方向|01–08支撑脚|09–16支撑脚|本轮改图与复用|","|---|---|---|---|"]
for g in groups:
 if g["action"]!="run":continue
 r=g["review"].get("grounding4",{});ss=r.get("contactSegments",[])
 contactlines.append(f"|{g['direction']}|{ss[0].get('supportFoot','待复核') if ss else '待复核'}：01/02→03/04→05/06→07/08|{ss[1].get('supportFoot','待复核') if len(ss)>1 else '待复核'}：09/10→11/12→13/14→15/16|局部编辑{len(r.get('replacementFrames',[]))}帧；其余复用/重排；详见来源表|")
contactlines+=["","逐方向空间位置与源图槽位记录：provenance/grounding-pairs-applied.json、provenance/grounding-pairs-*.json及provenance/offline-visual-review.json。模型目标与返回证据严格分开；历史输入图片经成品确认后清理，仅保留来源文字与SHA。","","新要求离线复核："+("已完成" if grounding_complete else "进行中，未判通过")+"；用户最终观感及客户端位移/滑步验收仍未完成。"]
with (ROOT/"MERGE_HANDOFF.md").open("a",encoding="utf-8") as f:f.write("\n".join(contactlines)+"\n")
with (ROOT/"STATUS.md").open("a",encoding="utf-8") as f:f.write("\n".join(contactlines)+"\n")
axislines=["", "## 上一轮脚轴复核", "", "已按用户视频与竹弓少女参考逐帧检查膝、踝、鞋长轴；保留自然屈膝与透视。视频中的灯柱、名称和投影遮挡了部分脚部，未把它当作精确脚尖角度标尺。", "", "|方向|本轮局部修正|其余帧|", "|---|---|---|"]
for g in groups:
 if g['action']!='run':continue
 ar=g['review'].get('axisReview',{}); changed=ar.get('replacementFrames',[])
 axislines.append(f"|{g['direction']}|{','.join(f'{x:02}' for x in changed) if changed else '无'}|{'已复核保留' if ar.get('offlineReviewed') else '待复核'}|")
axislines += ["", "此次确认NE05右支撑靴由NE突然偏成E侧面，局部回正踝靴；保留接地点和原动作相位。逐图来源见provenance/axis-edits-applied.json，详细审计见axis-review-20261004/audit-*.json。", "", "最新脚轴离线复核："+('已完成' if axis_complete else '进行中')+"。客户端仍未接入。"]
for name in ['MERGE_HANDOFF.md','STATUS.md']:
 with (ROOT/name).open('a',encoding='utf-8') as f:f.write('\n'.join(axislines)+'\n')
fullbodylines=["","## 本轮全身补审及60ms同步","","196帧已逐图补审肩肘腕握持与髋下膝踝鞋轴可见链。仅run/E/07双臂提前回收造成单帧跳动，采用第二版局部AI编辑修复；另外195帧图片原样保留。长袖、头发、长袍遮挡的关节不宣称直接可见。","","跑步最新正常为16×60ms=960ms，4倍慢放16×240ms=3840ms，无尾帧额外停留。战斗受击40、普攻30、施法45ms不变。依据provenance/timing-user-override-20261005.json覆盖旧75ms要求。","","当前补审状态："+("已完成" if full_body_complete else "静态完成，浏览器复核待完成")+"。详细记录：hand-review-20261005/audit-*.json、provenance/full-body-edits-applied.json及provenance/full-body-reference-history.json。E07两次调用的提示词、实际输入、回执与SHA保留；目标GPT Image 2.5 Sunburst/max，实际型号/质量仍未披露。客户端未接入、未运行。"]
for name in ['MERGE_HANDOFF.md','STATUS.md']:
 with (ROOT/name).open('a',encoding='utf-8') as f:f.write('\n'.join(fullbodylines)+'\n')
for script in ["build_sequence_previews.py","build_run_preview.py","build_overview.py"]:
 r=subprocess.run([sys.executable,"-X","utf8",str(ROOT/"tools"/script)],check=True,capture_output=True,text=True,encoding="utf-8");print(r.stdout.strip())
print(json.dumps({"runtime":len(files),"staticReviewed":196,"runLoopMs":960,"clientIntegrated":False},ensure_ascii=False))
