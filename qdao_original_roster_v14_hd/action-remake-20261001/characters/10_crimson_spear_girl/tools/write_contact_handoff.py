from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
old=R/'FINAL_REVIEW.md';history=R/'FINAL_REVIEW_BEFORE_SPATIAL_REVISION.md'
if not history.exists():history.write_bytes(old.read_bytes())
report=json.loads((R/'run-contact-revision-20261004/publish-report.json').read_text(encoding='utf-8'))
plan=json.loads((R/'RUN_CONTACT_PLAN.json').read_text(encoding='utf-8'))
text='''# 赤枪少女 · 接地修订完成检查

本轮按最新要求完成八方向跑步复修并发布到runtime。参考09竹弓少女的方向与腿部关系；同一支撑脚连续8帧，四个空间位置每处2张独立姿势，随后换脚8帧。位置指相对髋部沿运动轴逐步后移，末段允许前掌支撑。每帧75ms，16帧1200ms，无阶段权重、重复帧或额外圈尾停顿。

## 手脚与方向检查

E、NE、W、NW逐帧检查全身和脚部；NE15仅对独立新姿势的整体缩放漂移作头饰、髋部、枪身锚点注册，参数及原生SHA保留，没有脚底对齐。N06/07和14/15补足末位置后移并恢复红宝石靴饰。S06/07校正鞋宽与相邻位置关系。SE07/08及SW07/08重新保留原支撑腿，消除提前换腿和过大的脚位跳跃；分别沿高低靴、髋膝和胫骨追踪后确认连续。各方向复查两手握同一根完整长枪、脚尖朝向、靴饰和头身大小。未发现仍需返修的明确静态问题。

具体支撑播放位如下（每个逗号组为同一位置的两帧；左右指角色自身）：

| 方向 | 左脚四个位置 | 右脚四个位置 |
|---|---|---|
'''
for direction,g in plan['groups'].items():
    pairs=lambda k:' → '.join('/'.join(f'{n:02}' for n in pair) for pair in g[k])
    text+=f"| {direction} | {pairs('left')} | {pairs('right')} |\n"
text+='''
## 正式文件与预览验证

本次89个选择项包含原位保留和唯一重排，83个播放位的PNG发生变化。全196张正式PNG重新核对：1024×1024 RGBA、有效透明、alpha≥32主体不触边、文件SHA及像素均唯一、原生1254证据与逐图记录SHA一致。68张战斗动作PNG保持原SHA。

正式八方向同屏实际载入128/128，检查正常1×、慢放¼与逐帧；单方向512显示抽查SE08→09换脚、16→01首尾、手部与枪头。其他方向已在同屏、联系表及定向放大图检查。浏览器检查不是录屏逐像素运动测量，也不等于游戏客户端验收。

生成后的播放器JavaScript通过Node VM时序检查：八组75ms边界、1199→1200循环、完整16槽、缺槽禁播；preview/timing-verification.json记录实际结果。三个正式HTML全部图片引用核对当前runtime哈希，清理后再次验证，见preview/reference-verification.json。

## 当前入口和追溯

- 八方向同屏：preview/all-directions.html
- 全动作与单方向放大：preview/index.html
- 当前图片：runtime/
- 当前逐图清单与提示词索引：manifest.json（nativeGenerationRecord及promptReferenceFromNativeRecord）
- 本次发布与中断恢复记录：run-contact-revision-20261004/publish-report.json、publish-journal.json
- 战斗动作历史检查：FINAL_REVIEW_BEFORE_SPATIAL_REVISION.md

运行目录编号01起已是最终播放顺序，不能重复执行旧源帧重排。发布先持久化全部输出与来源文本，再写runtime，支持从同一暂存恢复。新1254图统一整画布缩至1024，不重复旧1254→860配准；NE15已注册1024图直接复制。

本次仍用内置image_gen。配置目标与实际提交/返回值分开记录；工具没有披露可核实model/quality，实际值为null。所有提示词、请求、回执、输入SHA、原生证据与逐图文字记录保留。按用户保留规则，核实成品与当前引用后清理原生、拒稿和过程图；旧selection和原图路径只作历史来源证据。清理结果见retention-report.json。

本次未修改客户端、其他角色或共享配置，未进行游戏内验收；用户最终验收尚未标记通过。
'''
old.write_text(text,encoding='utf-8')
p=R/'README.md';t=p.read_text(encoding='utf-8').replace('- [全动作预览](preview/index.html)','- [八方向同屏](preview/all-directions.html)\n- [全动作预览](preview/index.html)');p.write_text(t,encoding='utf-8')
print(json.dumps({'reviewUpdated':True,'changedRuntimeSlots':report['changedPixels']}))
