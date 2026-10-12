"""Write current human-readable handoff after reviewed export and cleanup."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
BATCH=ROOT/'provenance/limbs-20261004'
manifest=read(ROOT/'manifest.json')
selection=read(ROOT/'limbs-selection.json')
cleanup=read(BATCH/'cleanup-result.json')
assert manifest['limbsRevision']['status']=='exported_and_offline_reviewed'
assert cleanup['status']=='completed'
edited=len(selection)
rows='\n'.join(f"| {slot} | {v['reason']} |" for slot,v in sorted(selection.items()))
url='http://127.0.0.1:8818/preview/index.html?review=limbs-20261005'
status=f'''# 08 炼丹童子 · 当前交付状态

2026-10-05：现有196帧手脚与连续动作复查完成，本轮{edited}张修正已替换到正式资源。当前权威入口为manifest.json、limbs-selection.json、run-timing.json、runtime及preview/index.html。

- 跑步八方向各16帧，共128帧；按用户最新更正，正常1×每帧60ms，一圈960ms。
- 受击E/W各6帧、普攻E/W各12帧、施法E/W各16帧，共68帧；战斗交付方向为东、西，时长保持。
- 修正握瓶手前后摆动中缺失的身侧过渡，以及东北后蹬鞋尖的外撇；解剖右手丹炉、左手药瓶保持。
- 八向跑步保持原来的16/01跨循环配对、全部相位和编号；每对为两张独立姿态，没有复制帧或增加停顿。07→08为正常半圈换脚。

本轮替换清单（帧号保持不变，修前记录见provenance/limbs-20261004/before-manifest.json）：

| 正式槽位 | 修正内容 |
| --- | --- |
{rows}

196张1024×1024透明RGBA、196个不同图像及来源SHA、14组预览引用校验通过；14组×正常/慢放共28项播放时钟检查通过。离线逐帧、连续序列和浏览器重点复核完成；游戏客户端位移、滑步、切向和战斗事件尚未联调。

当前预览：{url}

本轮已清理{cleanup['removedImageCount']}张原生稿、拒稿及检查图，共{cleanup['removedBytes']:,}字节；保留196张正式图、14张当前联系表及全部来源文字。用户原视频、原截图未改动。

详细接入范围见MERGE_HANDOFF.md；当前支撑相位见RUN_PHASES.md；本轮复核、来源链及清理证据见provenance/limbs-20261004。
'''
(ROOT/'STATUS.md').write_text(status,encoding='utf-8')
handoff=f'''# 08 炼丹童子 · 当前动作交接

2026-10-05。完整手脚连续复查及定点修正已完成。以manifest.json、limbs-selection.json、run-timing.json、runtime和preview/index.html为准；早期选表/审阅保留历史证据，帧号没有重排。

## 正式资源

| 动作 | 方向 | 帧数 | 正常配时 |
| --- | --- | --- | --- |
| run | N/NE/E/SE/S/SW/W/NW | 各16，共128 | 960ms，每帧60ms |
| hit | E/W | 各6，共12 | 240ms，每帧40ms |
| attack | E/W | 各12，共24 | 360ms，每帧30ms |
| cast | E/W | 各16，共32 | 720ms，每帧45ms |

共196张1024×1024透明RGBA。逐帧SHA、独立来源、导出操作和相位在manifest及相邻generation.json闭合。战斗范围为E/W，不宣称其他六向战斗已制作。普攻事件标记06（150ms）；施法E09（360ms）、W10（405ms），客户端事件同步尚未验收。

## 本轮修正

全196帧已检查静态关节及相邻帧：髋→膝→踝→鞋尖运动平面、支撑与前掌蹬离、摆手路径、握持与遮挡。连续检查纠正了初次单帧审阅漏掉的握瓶手跳位，也重新确认NE后蹬的鞋尖外撇需要处理；早期“NE13–15全保留”结论由本轮替代。

| 正式槽位 | 修正内容 |
| --- | --- |
{rows}

其余图像像素保留。八向run保持原循环起点：右足16/01→02/03→04/05→06/07，左足08/09→10/11→12/13→14/15。07→08与15→16交接支撑足，16→01同足继续承重，无额外停顿。NW07→08经独立复核确认为正确半圈换脚；曾考虑过的起点旋转在执行前取消，未为了编号重画正常姿态。

本轮选表的originalInputSlot与finalSlot相同，前后SHA可对照provenance/limbs-20261004/before-manifest.json。按2026-10-05用户最新直接更正，八向run从75ms改为60ms，一圈960ms，每对120ms；相位和支撑足配对不变，战斗配时不变。前后配时SHA与依据见provenance/limbs-20261004/timing-correction.json。

## 参考、画布与验证

用户认可的弓足少女及原视频用于动作平面、接地和连续性的参考。视频24fps，复核连续片段0–31、88–119、148–179、283–314；小角色与遮挡限制精确鞋角测量。角色造型与画风保持项目确认风格，实际附图designs/jubaozhai-ui/02-characters.png。

新AI编辑均以当前runtime为底图，原生1254完整画布统一缩至1024，偏移0；不套旧940+(42,50)，不逐帧bbox贴合，不扭脚或整身平移。历史未改图仍以各自operation为准。逻辑根点(512,942)是摆放参考，942诊断线不是所有透视脚底必须贴齐的地面。

tools/verify_delivery.py核验196图、来源记录、透明通道和14组预览引用；tools/verify_preview_timing.cjs核验14组×1×/0.25×共28项，包括循环末帧和无额外停顿。浏览器正常/慢放与重点逐帧复核结果见provenance/limbs-20261004/review-result.json。预览地址：{url} 。

这是离线素材交付。小幅绘画轮廓差异仍可能存在；本机未进行客户端世界位移、滑步、跨向/idle切换和命中/特效同步验收，dynamicAccepted/clientValidated仍为false。

## 来源与清理

内置image_gen；2026-10-05核对官方最新目标为配置中的gpt-image-2.5-sunburst/max。工具不支持显式型号/质量参数，实际值未披露，记录null/未确认。每图提示词、输入、回执和来源记录保留在provenance及generation的limbs-20261004目录，来源链见edit-lineage.json。

本轮导出{edited}张修正图，已删除{cleanup['removedImageCount']}张原图、拒稿和检查图，共{cleanup['removedBytes']:,}字节，不留图片备份。当前保留196runtime与14preview联系表；原用户视频、截图未动；所有文字证据及接入文件保留。

可重跑rebuild_runtime_preview.py、verify_delivery.py、verify_preview_timing.cjs。所有依赖已删除原生稿或旧基线的历史apply/close脚本仅作制作记录，不可重跑，包括本轮apply_limbs_revision.py及close_limbs_revision.py；以后编辑从当前runtime建立新来源链。
'''
(ROOT/'MERGE_HANDOFF.md').write_text(handoff,encoding='utf-8')
timing=read(ROOT/'run-timing.json')
phase_rows='\n'.join(f"| {'解剖右足' if p['foot']=='right' else '解剖左足'} | {p['frames'][0]:02} → {p['frames'][1]:02} | {p['position']} | 120ms |" for p in timing['contactPairPlan'])
phases=f'''# 08 跑步当前相位

2026-10-05。八方向采用相同支撑位置顺序，按各向遮挡和透视绘制。每个位置为两张独立姿态；当前时长与相位以run-timing.json为准。

| 支撑足 | 当前帧号 | 支撑位置与动作 | 时长 |
| --- | --- | --- | --- |
{phase_rows}

正常16×60ms=960ms，0.25×为3840ms。07→08、15→16交接支撑足；16→01同足由初接触过渡到承重，无额外停顿。另一足自然屈膝前摆。鞋尖随髋→膝→踝的行进平面，前掌推蹬允许自然抬跟，不能把露出鞋底等同外翻。

本轮保留所有帧号与相位；独立复核解除NW07/08提前换脚的疑点，未改变正确循环起点。时长按用户最新更正统一为60ms，覆盖此前75ms记录；依据和前后SHA见provenance/limbs-20261004/timing-correction.json。

已复核八向完整半圈、接地配对及相邻手部路径。解剖右手丹炉、左手药瓶通过肩袖追踪确认。根点(512,942)用于摆放，诊断线并非各透视脚底的统一地面；新修图完整画布缩至1024、偏移0，无逐帧贴脚平移。

正式联系表为preview/run-方向-contact.png，复核证据见provenance/limbs-20261004/review-result.json。当前为离线动作判断，游戏世界坐标中的位移、滑步和跨方向衔接尚未联调。
'''
(ROOT/'RUN_PHASES.md').write_text(phases,encoding='utf-8')
print(json.dumps({'documents':['STATUS.md','MERGE_HANDOFF.md','RUN_PHASES.md'],'editedFrames':edited}))
