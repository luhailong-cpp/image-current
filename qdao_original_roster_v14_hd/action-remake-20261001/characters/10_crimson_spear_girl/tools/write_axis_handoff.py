from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
W=R/'run-axis-revision-20261004'
def load(p): return json.loads(p.read_text(encoding='utf-8'))
report=load(W/'publish-report.json')
validation=load(R/'validation.json')
browser=load(W/'browser-review.json')
assert report['status']=='applied' and validation['status']=='passed' and browser['status']=='passed'
previous=(W/'previous-FINAL_REVIEW.md').read_text(encoding='utf-8')
table=previous[previous.index('| 方向 |'):previous.index('## 正式文件与预览验证')].strip()
text=f'''# 赤枪少女 · 腿脚朝向修订检查

2026-10-04。本轮按用户视频和方向反馈完成定向修订，已发布至 runtime 并刷新三个正式预览。先前接地修订记录保留在 run-axis-revision-20261004/previous-FINAL_REVIEW.md；本文件描述当前结果。

## 当前动作规则

参照09竹弓少女的方向及支撑关系。同脚支撑8帧：前端2帧、中间4帧、后端2帧，即沿运动轴相对髋部推进的四个位置各2张独立姿势；随后另一脚8帧。末位置允许前掌支撑。每帧75ms，16帧1200ms，无阶段权重、重复帧、插值或圈尾停顿。

{table}

## 本轮具体修正

- NE15、16、01：悬空脚从鞋头突然反转朝镜头，改为连续的后跟、鞋底与侧面关系；保留原右支撑腿，16高抬腿、01下放仍为独立姿势。
- SW08：去除高处悬空靴整片鞋底突然朝镜头的跳变，延续07鞋面朝向并保留08较高抬膝。
- W06：后侧悬空腿自然屈膝回收，消除05→06→07多出的向后踢；地面支撑腿保留。
- NW10、11、12：修复腿部遮挡及支撑连接，避免09之后读成提前换脚；同一支撑腿持续至12，再于13换脚。

八方向逐帧审查，定向修图另看相邻帧和完整角色。双手握枪、长枪完整性、头身大小及透明留白一并复核。E、N、S、SE未发现同等级明确的鞋掌反转，保留原帧。正常屈膝、抬跟和斜视透视不强行拉成二维直线。NE11–12摆腿横向展开、SW15–16轻微鞋面角度变化，属于未能仅凭二维像素定性的观察项，未作为确定错误重画。

实际解码用户原视频418帧，并检查连续固定人物裁切。参考角色较小且名称/阴影遮挡脚部；视频用于运动平面和连续性判断，不作为精确三维踝角或逐像素匹配证据。逐方向原始检查文字保留在本轮 EN-audit、WN-audit、S-diagonal-audit、NS-axis-review.md。

## 导出与本机检查

本轮替换{report['changedPixels']}张正式跑步PNG。全部196张仍为1024×1024 RGBA，有效透明、主体alpha≥32不触边、文件SHA与像素均唯一；原生1254证据和生成记录SHA逐项校验。68张受击、普攻和施法成品保持发布前SHA。

新选图整张1254画布等比缩至1024，不套用旧860缩放、不按脚底贴线。运行编号01起已经是播放顺序，不再次执行旧重排。发布前持久保存完整输出和来源文本，发布日志完成后才允许清理，清理还核对validation绑定的当前清单SHA。

浏览器检查详情见 run-axis-revision-20261004/browser-review.json；实际加载正式资源，检查正常1×、慢放¼及修改帧段逐帧。三个HTML引用核对当前runtime哈希，清理后再次验证。播放器JavaScript的八方向75ms边界、1199→1200首尾循环与缺槽禁播测试见 preview/timing-verification.json。另修复首次图片载入时动画时间戳早于载入回调、导致负帧号和同屏停播的问题；两播放器钳制负时间差，同屏增加空图守卫，首次载入、正常/慢速和逐帧回归见 preview/overview-timing-verification.json。本机渲染检查不等于游戏内验收。

## 成品与来源

- 八方向同屏：preview/all-directions.html
- 全动作与单方向放大：preview/index.html、preview/timing-grounding.html
- 当前图片与清单：runtime/、manifest.json、delivery-current.json
- 本轮发布记录：run-axis-revision-20261004/publish-report.json、publish-journal.json
- 逐图提示词：manifest.json 的 nativeGenerationRecord 指向生成记录，其中 prompt 指向原提示词

使用内置 image_gen，实际 model/quality 未披露，记录为null；配置目标、提交参数和返回证据分别保存。提示词、输入SHA、请求、回执、原生SHA及逐图记录均保留。原生、拒稿和过程图片在验证当前资源完整后按用户规则清理；其路径只保留作历史出处，当前预览不依赖它们。清理见 retention-report.json，前次清理文字清单也保留在本轮目录。

仅修改本角色目录。客户端未接入，未修改其他角色、共享配置或Git状态。用户最终验收未标记通过。
'''
(R/'FINAL_REVIEW.md').write_text(text,encoding='utf-8')
print(json.dumps({'review':'FINAL_REVIEW.md','axisSlots':report['selectedSlots'],'changedPNG':report['changedPixels']}))
