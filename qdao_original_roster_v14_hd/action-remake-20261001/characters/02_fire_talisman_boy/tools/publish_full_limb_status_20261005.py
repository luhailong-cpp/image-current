from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
read=lambda p:json.loads((R/p).read_text(encoding='utf-8'))
review=read('reviews/full-limb-final-20261005.json')
assert review['reviewedFrames']==196 and not review['knownUnresolvedArtFailures']
assert read('inventory.json')['offline_materials_complete']
assert read('reviews/full-source-chain-audit.json')['pass']
changed='、'.join(p.replace('frames/','').replace('.png','') for p in review['changedPaths']) or '无'
for p in ['tools/run-grounding-template.html','previews/run-grounding.html']:
 f=R/p;s=f.read_text(encoding='utf-8');s=s.replace('2026-10-05 全动作手脚复核进行中，北向支撑脚轴正在修正；客户端未接入。','2026-10-05 全部196张手脚已重新看图复核，支撑脚轴修正已更新；客户端未接入。').replace('全动作手脚复核进行中','全动作手脚离线复核完成');f.write_text(s,encoding='utf-8')
alias='previews/run-eight-directions-full-limb-20261005.gif'
shutil.copyfile(R/'previews/run-eight-directions.gif',R/alias)
sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
(R/'previews/full-limb-overview-source.json').write_text(json.dumps({'createdAtUtc':datetime.now(timezone.utc).isoformat(),'file':alias,'sha256':sha(alias),'operation':'byte-identical preview alias to avoid earlier chat-image caching','derivedFrom':'previews/run-eight-directions.gif','sourceSha256':sha('previews/run-eight-directions.gif'),'sourceMap':'previews/contact-sources.json','formalSourceFrames':128,'frameMs':60,'cycleMs':960,'gifQuantization':'GIF and HTML uniform60ms, total960'},ensure_ascii=False,indent=2),encoding='utf-8')
(R/'STATUS.md').write_text(f'''# 02 火符少年当前进度

2026-10-05：本轮196张全部动作、全部方向手脚重新看图复核完成。局部重画{review['changedFrames']}张，保留{review['retainedFrames']}张；本轮替换槽位：{changed}。

检查肩—肘—腕—握柄的连接、解剖右手五张红符扇与左手单铜铃，及髋—膝—踝—鞋头的运动平面；保留自然屈膝、重量转移和透视。完整逐帧当前SHA与结论见reviews/full-limb-final-20261005.json，14组动作的正常/慢放浏览器抽样及控件检查见reviews/full-limb-browser-20261005.json。文件数和SHA不代替美术判断。

共196张1024×1024 RGBA正式PNG：跑步128、受击12、普攻24、施法32。跑步正常16×60ms=960ms、慢放3840ms，同一支撑脚每个相对位置两张独立姿态；按2026-10-05本聊天最新用户要求采用60ms，覆盖旧75ms。受击240ms、普攻360ms、施法720ms保持。逐图来源与导出像素审计另见reviews/full-source-chain-audit.json。

上一轮2026-10-04视频脚轴修订曾替换25张跑步；其历史报告保留，新一轮以full-limb-final-20261005.json的196张SHA为准。

交付：previews/index.html（四动作）、previews/run-grounding.html（八向跑步）、MERGE_HANDOFF.md、MERGE_FILES.csv。正式游戏图在frames/，仅修改本角色目录，未操作共享Git暂存/提交/推送。

本批使用内置image_gen，目标GPT Image 2.5 Sunburst/max；工具未开放型号/质量选择器且未披露实际值，逐图记未确认。没有收费API/CLI调用。

客户端尚未接入，游戏内滑步、位移、根点、碰撞与事件同步未验。此前过程图批量清理被自动审批以“blocked by policy”拒绝，未给具体理由；过程图暂留，未绕过重试，见reviews/cleanup-blocked.json。
''',encoding='utf-8')
print({'reviewed':196,'changed':review['changedFrames'],'alias':alias})
