from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parents[1]
W=R/'full-limb-review-20261004'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=load(W/'publish-report.json')
v=load(R/'validation.json')
browser=load(W/'browser-review.json')
review=load(W/'current-frame-review.json')
assert report['status']=='applied' and v['status']=='passed' and browser['status']=='passed'
assert review['reviewedCurrentFrames']==196 and review['knownUnresolvedFailures']==0
assert review['inventorySHA256']==v['inventorySHA256']==sha(R/'delivery-current.json')
changed=report['changedPixels']
bullets='\n'.join('- '+x for x in review['changeSummary'])
text=f'''# 赤枪少女 · 全动作手脚复核

2026-10-05。196张当前成品均经过实际画面检查，本轮替换{changed}张跑步帧。审查当前SHA逐帧记录见 full-limb-review-20261004/current-frame-review.json。像素、帧数与来源验证不代替肢体视觉检查。

## 本轮修正

{bullets}

N/S、NE/SE和战斗动作中没有发现需重画的明确可见手脚错误；已确认正确的帧保持原SHA。NW01/04及新16下枪尾被遮挡，不能直接量出全杆轴；NW08的下杆部分受靴子遮挡。NW09/10金尾装饰长度存在小幅画面差异，实际外露黑杆中心线已复核。未把这些遮挡或装饰差异当作已看清的关节错误。宽袖、裙摆和头发遮住的肩肘、髋部并非全部可见；本检查不宣称量得精确三维关节角。

## 跑步动作与播放

参照09竹弓少女和用户视频的方向、连续支撑关系。沿运动轴逐步经过连续位置，每处两张独立姿态；四处后换另一脚，保留膝踝弯曲与末段前掌推蹬。具体起止编号见RUN_CONTACT_PLAN.json。全方向均为16×60ms=960ms，无阶段加权、重复帧、插值或圈尾停顿。

实际复核髋膝踝与鞋尖的运动平面、腿部遮挡归属、肩袖到手腕的可见连接、手掌握持和长枪杆段连贯性。正常透视、自然屈膝、抬跟与鞋底在悬空时可见，不强行改成二维直线。

## 成品验证

196张均为1024×1024 RGBA，完整透明，有效主体不触边，文件SHA和解码像素均唯一；原生1254图的SHA、逐图生成记录及当前清单逐项核对。68张战斗帧本轮保持原SHA。新版三份HTML全部指向当前runtime哈希；正常1×、慢放¼、暂停与逐帧已实际在浏览器检查。时序自动检查覆盖60ms边界、首尾循环和首次载入时间差。详情见validation.json、preview/timing-verification.json、preview/overview-timing-verification.json和本轮browser-review.json。

本轮内置image_gen独立局部重绘，完整1254画布等比导出1024；如有配准，其具体处理以逐图记录为准。未复制、镜像或插值补帧。播放编号已经落入runtime，不得再应用历史重排。客户端尚未接入，本机预览不等于游戏内验收。

## 来源与保留

manifest.json的nativeGenerationRecord逐图链接到模型目标、实际参数、提示词、参考SHA与返回记录。实际model/quality未由宿主披露，明确记为null，不把配置目标当实际版本。使用内置生图，未调用收费API/CLI。

确认当前资源引用完整后，原生、拒稿及加工中间图片按用户保留规则清理；文字来源证据保留，清理见retention-report.json。历史路径只作出处，不是当前加载依赖。当前正式图只在runtime与preview。
'''
(R/'FINAL_REVIEW.md').write_text(text,encoding='utf-8')
table='''| 动作 | 方向数 | 每方向帧数 | 每帧 | 一圈 |
|---|---:|---:|---:|---:|
| 跑步 | 8 | 16 | 60ms | 960ms |
| 受击 | 2 | 6 | 40ms | 240ms |
| 普攻 | 2 | 12 | 30ms | 360ms |
| 施法 | 2 | 16 | 45ms | 720ms |'''
handoff=f'''# 赤枪少女 · 成品交接

196张动作成品已完成本轮全动作手脚复核，替换{changed}张跑步帧。当前图片runtime/，逐图清单manifest.json和delivery-current.json。客户端尚未接入。

{table}

跑步连续支撑位置各两张独立姿态，沿真实运动方向推进。运行目录编号01起已是播放顺序，不可再次应用历史源帧重排。所有图片1024×1024 RGBA，保持各帧独立姿势。普攻06为接触标记，施法09为释放标记。

本轮内容：
{bullets}

预览：preview/index.html为全部动作；preview/all-directions.html为八方向同屏；preview/timing-grounding.html为跑步放大逐帧。均支持正常、¼慢放、暂停和逐帧。

检查范围及限制见FINAL_REVIEW.md；逐帧当前SHA判读见full-limb-review-20261004/current-frame-review.json；发布来源见同目录publish-report.json与publish-journal.json。客户端接入时需再验证世界坐标、地面层级及动作状态切换。

原生1254输出和1024导出分开记录。每张图片旁generation.json保留来源SHA；manifest.json的nativeGenerationRecord可查提示词和内置工具回执。实际模型和质量没有披露，记录为null。成品验证后清理原图、拒稿和过程图，只留正式图及文字来源，见retention-report.json。
'''
(R/'MERGE_HANDOFF.md').write_text(handoff,encoding='utf-8')
(R/'STATUS.md').write_text(f'# 赤枪少女 · 当前状态\n\n196/196张完成本轮全动作手脚复核，修订{changed}张跑步帧。跑步16×60ms=960ms。当前资源runtime/，预览preview/index.html。客户端未接入。\n\n见FINAL_REVIEW.md、validation.json和full-limb-review-20261004/current-frame-review.json。\n',encoding='utf-8')
(R/'README.md').write_text(f'''# 赤枪少女动作成品

196张1024×1024 RGBA已完成本轮手脚复核；本轮修订{changed}张跑步帧。跑步各方向16×60ms=960ms。客户端尚未接入。

- [全部动作预览](preview/index.html)
- [八方向同屏](preview/all-directions.html)
- [跑步逐帧检查](preview/timing-grounding.html)
- [成品逐图清单与来源索引](manifest.json)
- [手脚检查记录](FINAL_REVIEW.md)
- [交接说明](MERGE_HANDOFF.md)
- [像素和来源校验](validation.json)

每张成品旁generation.json关联原生来源、模型和质量的实际披露情况。manifest.json的nativeGenerationRecord再链接该图提示词与回执。内置工具未披露型号/质量的记录为null；原图清理不改写这些历史文字证据。
''',encoding='utf-8')
manifest=load(R/'manifest.json')
manifest.update(fullLimbRevision='20261005-anatomy',fullLimbReview='full-limb-review-20261004/current-frame-review.json',revisedRunFrameCount=changed)
write(R/'manifest.json',manifest)
write(W/'completion.json',{'status':'complete','completedAt':datetime.now(timezone.utc).isoformat(),'inventorySHA256':sha(R/'delivery-current.json'),'reviewedCurrentFrames':196,'changedRuntimePNGs':changed,'knownUnresolvedFailures':0,'browserReview':'full-limb-review-20261004/browser-review.json','clientIntegrated':False,'userFinalAcceptance':False})
print(json.dumps({'currentReview':196,'changedFrames':changed,'completion':'complete'}))
