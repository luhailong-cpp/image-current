"""Build factual delivery snapshot and complete-sequence previews; no runtime image edits."""
import json,hashlib
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image,ImageDraw,ImageFont
from current_review_state import current_review
from current_run_pairs import current_run_pairs
R=Path(__file__).resolve().parents[1]
SPECS={"run":(["N","NE","E","SE","S","SW","W","NW"],16,60),"hit":(["E","W"],6,40),"attack":(["E","W"],12,30),"cast":(["E","W"],16,45)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 frames=[];seq=[];preview=[];font=ImageFont.truetype("C:/Windows/Fonts/msyh.ttc",18);labels={"run":"跑步","hit":"受击","attack":"普攻","cast":"施法"}
 for a,(dirs,count,ms) in SPECS.items():
  for d in dirs:
   present=[];missing=[]
   for n in range(count):
    p=R/"runtime"/a/d/f"{n:02d}.png"
    if not p.exists():missing.append(n);continue
    try:
     im=Image.open(p);im.load()
     rec=p.with_name(p.name+".generation.json")
     gen=json.loads(rec.read_text(encoding="utf-8-sig")) if rec.exists() else None
     row={"action":a,"direction":d,"frame":n,"path":p.relative_to(R).as_posix(),"sha256":sha(p),"size":list(im.size),"mode":im.mode,"generationRecord":rec.relative_to(R).as_posix() if rec.exists() else None,"durationMs":ms,"review":"静态候选；整段动态待验收","native":gen.get("native") if gen else None,"actualModel":None,"actualQuality":None}
     frames.append(row);present.append(n)
    except (OSError,ValueError):missing.append(n)
   row={"action":a,"direction":d,"expected":count,"exported":len(present),"missing":missing,"durationMs":ms,"segmentMs":count*ms,"dynamicReview":"pending","client":"not_integrated"}
   if not missing:
    sequence=[]
    for n in present:
     im=Image.open(R/"runtime"/a/d/f"{n:02d}.png").convert("RGBA").resize((640,640),Image.Resampling.LANCZOS)
     bg=Image.new("RGBA",(640,684),(32,42,55,255));bg.alpha_composite(im,(0,0))
     draw=ImageDraw.Draw(bg);draw.text((18,652),f"{labels[a]} {d}  {n:02d}/{count-1:02d} | 原帧{ms}毫秒 | 本机素材",font=font,fill=(230,230,230))
     sequence.append(bg.convert("RGB"))
    for suffix,factor in [("normal",1),("slow",4)]:
     out=R/"preview"/f"{a}_{d}_{suffix}.webp"
     sequence[0].save(out,save_all=True,append_images=sequence[1:],duration=ms*factor,loop=0,lossless=True,method=4)
     preview.append({"path":out.relative_to(R).as_posix(),"sha256":sha(out),"action":a,"direction":d,"speed":1/factor,"derivedFrom":[f["path"] for f in frames if f["action"]==a and f["direction"]==d],"operation":"fixed full-canvas resize to640, opaque preview background and frame labels; no interpolation"})
    row["preview"]=[f"preview/{a}_{d}_normal.webp",f"preview/{a}_{d}_slow.webp"]
   seq.append(row)
 now=datetime.now(ZoneInfo("America/New_York")).isoformat(timespec="seconds")
 review=current_review()
 out={"character":"06_thunder_caster_boy","updatedAt":now,"expected":196,"exportedCandidates":len(frames),"visualFinalApproved":0,"dynamicApproved":0,"clientIntegrated":False,"complete":False,"generationTarget":{"model":"gpt-image-2.5-sunburst","quality":"max"},"actualModel":None,"actualQuality":None,"unverifiedReason":"host-managed built-in route, no model/quality selector or result disclosure","anchor":{"canvas":[1024,1024],"root":[512,942],"unityPivot":[0.5,0.08],"status":"provisional, requires visual sequence and client verification","policy":"fixed full canvas, preserve flight; no per-frame lowest-pixel alignment"},"events":{"hit":{"impactFrame":1,"peakRecoilFrame":2},"attack":{"contactFrame":6},"cast":{"releaseFrame":9},"run":{"contacts":[0,8],"flight":[4,5,12,13]}},"eventsStatus":"planned phase indices, verify actual poses before client","sequences":seq,"files":frames,"previews":preview}
 pairs=current_run_pairs()
 out['events']['run']={'currentFramePositionObservations':pairs,'pairDurationMs':120,'clientEventsCalibrated':False,'obsoleteContactAndFlightIndicesRemoved':True}
 out['eventsStatus']='run依据当前图片的位置段逐帧列出；战斗事件为素材建议点，客户端尚未标定'
 out['anchor']['policy']='fixed full canvas, preserve authored stance and motion; no per-frame lowest-pixel alignment'
 out['runTimingReview']={'requestDate':'2026-10-05','selectedNormalCycleMs':960,'uniformFrameMs':60,'durationsMs':[60]*16,'speedOptions':[1,0.25],'oldFastOptionsRemoved':True,'status':'同一支撑脚持续接地、相对位置每两张独立姿态推进；16帧均匀60ms，客户端未接入','preview':'preview/timing-grounding-20261003/index.html','referenceGroundVerified':False,'clientVerified':False}
 if review:
  if 'retentionCleanup' in review:out['retentionCleanup']=review['retentionCleanup']
  out.update(complete=review.get('localWorkComplete',False),completionScope='本机素材、手脚逐帧复核、离线预览、逐图来源与合并交接；不含客户端接入或用户最终观感批准',staticReviewedFrames=196,offlinePlaybackVerifiedSequences=14,currentReview='review/CURRENT_REVIEW.json',userFinalApproved=False)
  for f in frames:f['review']='当前手脚逐帧复核完成，离线正常/慢放和逐帧功能已验证，客户端未接入'
  for s in seq:s['dynamicReview']='offline_playback_verified; user/client acceptance pending'
 (R/"STATUS.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 lines=["# 06 雷法少年 · 合并交接","","更新时间："+now,"","当前为制作中候选帧包。生成/导出数量见下表，完整美术动态与客户端验收另行记录；合并时逐文件比较另一电脑资源。","","|动作|候选导出/目标|","|---|---:|"]
 for a,(dirs,c,ms) in SPECS.items():lines.append(f"|{a}|{sum(s['exported'] for s in seq if s['action']==a)}/{len(dirs)*c}|")
 lines+=["","逐帧路径、SHA256、原生尺寸及来源记录索引见 [STATUS.json](STATUS.json)；正常/慢速/逐帧查看 [preview/index.html](preview/index.html)。完整序列才生成WebP连播，缺槽为空。脚向/握持逐动作复核见review，自动播放证据不等于美术通过。","",
 "候选正式尺寸1024×1024 RGBA，来源为单人原生至少1024；全画布等比降采样，无镜像、变形或插值补帧。根锚点暂定(512,942)，Unity pivot(0.5,0.08)，需整段检查及客户端最终确认。run正常1×为60ms/帧、960ms/圈，按用户最新要求已用于素材预览与清单；客户端未接入；hit40ms，attack30ms，cast45ms。普攻接触计划06，施法释放计划09，真实阶段仍须验收。",
 "","目标GPT Image2.5 Sunburst / max。内置入口没有型号/质量选择器，实际提交model/quality及实际返回型号/质量均未确认；逐图记录保存真实参数、提示词和参考。未使用收费API/CLI。",
 "","合并只取本角色目录新增/修改文件；保留另一电脑分歧供用户比较，不触碰其他角色或共享Git。客户端未接入、未运行验收。2026-10-03末只读确认本机客户端目录现已存在；本任务仍仅写角色私有目录，未接入或运行客户端。",
 "","剩余：补全STATUS所列缺槽；修正单帧和整段检查发现的问题；复核跨动作比例、跨方向持手、根锚点、alpha边缘、首尾衔接；通过后清除已淘汰原图，仅保留来源文字记录和正式/当前在制资源。"]
 lines += ['', '## 2026-10-03 跑步接地与节奏更新', '', '用户指定正常跑步每圈960ms，16帧均匀60ms，精确整除；当前正式选项已移除480/640/720/800ms快档。保留正常、慢放、暂停与逐帧，不在首尾额外停顿。受击、普攻、施法节奏保持原值。', '', '[本角色960ms正常与慢放](preview/timing-grounding-20261003/index.html) · [逐帧来源与当前时长](preview/timing-grounding-20261003/review-data.json)。离线默认240像素，实际客户端显示尺寸/位移速度未确认。', '', '所有八方向帧组仍按各自复核状态交接。需按实图确认两侧接触、承重、身体经过与后侧蹬离，不能套用07角色帧号或权重。根点(512,942)是历史暂定值，未完成实际标定；不能据此宣称脚已着地。逐方向相位、手脚修正与未解决项见review中的对应记录。原CUA浏览器入口不可用；本机Edge headless已实际播放并采样，见review/headless_grounding_review_20261003.md。此证据仅覆盖其记录SHA对应快照，证明页面时序与解码，不等同美术通过。']
 if review:
  lines[4]='本机196帧素材、手脚修正、离线预览和来源交接已完成。实际对照用户指定09竹弓少女当前版本逐向检查，具体保留/修正项与当前SHA见 [CURRENT_REVIEW.json](review/CURRENT_REVIEW.json)。客户端未接入，用户最终观感批准未代为填写。'
  lines=[x if not x.startswith('剩余：') else '接入待办：由用户在另一电脑逐文件合并；客户端标定根点、位移速度、触地/命中/释放事件并作游戏内验收。当前素材不再有缺槽，合并前可直接查看八方向960ms动态图与全部动作预览。' for x in lines]
  lines += ['', '## 当前离线验收', '', '[八方向正常动态图](preview/run-eight-directions-960.webp) · [四分之一慢放](preview/run-eight-directions-3840.webp) · [全部动作正常/慢放/逐帧](preview/index.html)。', '', '最新完整播放器证据：['+review['playbackEvidence']+']('+review['playbackEvidence']+')。记录14段正常及慢放、暂停与逐帧首尾，绑定196张当前SHA。自动时序检查不替代用户最终动态观感确认。']
 lines += ['', '## 2026-10-04 最新接地位置安排', '', '用户解释为“直脚着地两帧，再旁边点两帧，再旁边点两帧，再旁边点俩帧，依次类推”。当前按同一支撑脚从前端落地、前侧承重、身体经过、后侧蹬离的四个相对位置段推进，每段两张独立姿态，共八张，然后另一脚交替；位置沿各方向运动与透视变化，鞋尖不向外撇。此条替代旧中间四帧分配及旧固定腾空索引。', '', '各向为了保留可用姿态采用不同相位起点。当前逐帧对应支撑脚、位置段与来源见 STATUS.json 中 events.run.currentFramePositionObservations；只有与当前 PNG 的 SHA 一致的复核记录才进入此表。播放器暂停逐帧也显示同一信息。']
 (R/"MERGE_HANDOFF.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
 from write_final_handoff import write_handoff
 write_handoff(out)
 print(json.dumps({"exportedCandidates":len(frames),"completeSequences":sum(not s["missing"] for s in seq),"animatedPreviews":len(preview),"dynamicApproved":0},ensure_ascii=False))
if __name__=="__main__":main()


