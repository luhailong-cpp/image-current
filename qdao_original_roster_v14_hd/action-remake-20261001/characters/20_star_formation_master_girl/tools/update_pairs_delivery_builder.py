from pathlib import Path
p=Path(__file__).resolve().parent/"build_delivery.py"
s=p.read_text(encoding="utf-8")
s=s.replace("八方向每次连续4帧真实接地的新要求仍在复核/修正","八方向同脚8帧、四位置各2帧的新要求仍在复核/修正")
s=s.replace("- 固定完整原生画布缩放到922×922，偏移(51,40)，根点(512,922)。没有逐帧最低像素贴地、bbox缩放、镜像或插值补帧。","- 画布1024×1024，根点(512,922)。旧保留图沿用原固定画布变换；本轮以既有最终构图为编辑输入，新原生返回按完整画布等比导出1024，不重复套用旧922缩放。各图operation逐项记录；没有逐帧最低像素贴地、bbox缩放、镜像或插值补帧。")
start=s.index('contactlines=["","## 连续接地复核')
end=s.index('for script in ["build_sequence_previews.py"',start)
s=s[:start]+'''contactlines=["","## 最新两帧一位置接地复核","","同一支撑脚连续8帧，前落、身下、后侧、后蹬各2张独立姿态；再换另一脚同样8帧。每对150ms，半圈600ms，整圈1200ms。真实姿态无重复图、插值或加停顿。","","|方向|01–08支撑脚|09–16支撑脚|本轮改图与复用|","|---|---|---|---|"]
for g in groups:
 if g["action"]!="run":continue
 r=g["review"].get("grounding4",{});ss=r.get("contactSegments",[])
 contactlines.append(f"|{g['direction']}|{ss[0].get('supportFoot','待复核') if ss else '待复核'}：01/02→03/04→05/06→07/08|{ss[1].get('supportFoot','待复核') if len(ss)>1 else '待复核'}：09/10→11/12→13/14→15/16|局部编辑{len(r.get('replacementFrames',[]))}帧；其余复用/重排；详见来源表|")
contactlines+=["","逐方向空间位置与源图槽位记录：provenance/grounding-pairs-applied.json、provenance/grounding-pairs-*.json及provenance/offline-visual-review.json。模型目标与返回证据严格分开；历史输入图片经成品确认后清理，仅保留来源文字与SHA。","","新要求离线复核："+("已完成" if grounding_complete else "进行中，未判通过")+"；用户最终观感及客户端位移/滑步验收仍未完成。"]
with (ROOT/"MERGE_HANDOFF.md").open("a",encoding="utf-8") as f:f.write("\\n".join(contactlines)+"\\n")
with (ROOT/"STATUS.md").open("a",encoding="utf-8") as f:f.write("\\n".join(contactlines)+"\\n")
''' +s[end:]
p.write_text(s,encoding="utf-8")

