# 天音少女 · 素材接入交接

2026-10-05本轮素材交付已完成：196张正式1024×1024 RGBA、14段动作，审查范围覆盖全部帧的腿脚及肩肘腕握持。已替换17张：14张run脚轴局部修正，以及hit/W03–05的远侧RIGHT手修正；其余114张run和65张combat保留。正式提升、浏览器复验和清理后文件核验均通过，见[本轮收尾记录](provenance/foot-axis-20261004/closeout.json)。客户端尚未接入，也未进行游戏运行验收。

## 当前交付与接地帧

以[final/manifest.json](final/manifest.json)及[final-selection.json](final-selection.json)为当前入口。图片为`final/<action>/<direction>/<两位帧号>.png`，同名`.png.generation.json`保存来源、导出变换、SHA和验收记录。196个原生来源SHA和196个正式PNG的SHA各自唯一。历史选表及已删除中间图不作为加载入口。

跑步01–08连续由RIGHT支撑，09–16连续由LEFT支撑；每组依次为前部落脚、身体经过、髋下向后、后侧前掌蹬地，各占两张独立姿态。逐帧`supportLeg`与`stancePosition`保留在正式清单和sidecar。08→09、16→01换腿；按裤腿遮挡追踪真实腿属，不把屏幕左右或鞋底最低位置当作腿身份。

| 动作 | 方向 | 每方向帧数 | 帧时长 | 总时长 |
| --- | --- | --- | --- | --- |
| run | N/NE/E/SE/S/SW/W/NW | 16 | 60ms | 960ms |
| hit | E/W | 6 | 40ms | 240ms |
| attack | E/W | 12 | 30ms | 360ms |
| cast | E/W | 16 | 45ms | 720ms |

[animation-timing.json](animation-timing.json)为时长配置，首尾不额外停留、不应用分相位权重。战斗仅hit/W03–05局部修手，其他65张战斗图保留；跑步按最新要求为60ms/帧、960ms/圈；战斗时长不变。既有触弦事件建议保持：attack E04起90ms首次触弦、E05起120ms重拍；attack W05起120ms；cast E/W09起360ms释放。客户端伤害、特效和音效事件尚未接线。

## 配准与来源

全196帧共用0.65比例、每段动作/方向固定源根，目标根(512,942)，底部原点pivot[0.5,0.080078125]，见[registration.json](registration.json)。没有按每帧脚底、头顶或包围盒移动缩放；远近脚保持透视差。前掌蹬地仍属于接地，不要求远近脚落在同一屏幕水平线。

正式PNG规格为1024 RGBA、边缘alpha为0。本轮局部修图原生为1254×1254，采用固定预乘Alpha重采样。膝踝和鞋轴沿动作平面自然衔接，保留屈膝而非锁膝；解剖RIGHT手拨琴下弦、LEFT手扶琴上段。被头发、宽袖和身体遮住的关节，不声称直接可见。

本轮修图通过宿主内置image_gen执行，配置目标GPT Image 2.5 Sunburst/max；工具未披露实际型号/质量，实际字段null，不能据目标值声称已显式锁定模型。当前来源构成为194个本批新绘来源和2个保留旧来源。累计成功生成数由收尾脚本按399基础加本轮证据目录中的唯一原生SHA计算，拒稿计入成功生成但不计入当前选图。逐图sidecar内嵌原始来源；[196帧提示词与来源汇总](provenance/foot-axis-20261004/selected-prompt-set.json)保留每帧原有入口和证据，历史提示词缺失不补造。

## 核验与清理

- [本轮实图验收](provenance/foot-axis-20261004/acceptance.json)：全部196帧静态审查及17张局部修正，绑定候选与替换前SHA。
- 跑步脚轴审查：[E/W](provenance/foot-axis-20261004/audit-EW.json)、[N/NE/SE](provenance/foot-axis-20261004/audit-NESEN.json)、[S/SW/NW](provenance/foot-axis-20261004/audit-SWNWS.json)；[跑步肩肘腕](provenance/foot-axis-20261004/audit-run-arms.json)。
- 战斗逐帧审查：[受击](provenance/foot-axis-20261004/audit-hit.json)、[普攻](provenance/foot-axis-20261004/audit-attack.json)、[施法](provenance/foot-axis-20261004/audit-cast.json)；修前发现的问题由验收中的选定修图逐一关闭。
- [正式提升记录](provenance/foot-axis-20261004/promotion.json)：只替换已接受的17张，保留其余179张正式图。
- [浏览器检查](provenance/foot-axis-20261004/browser-check.json)：实际时序与疑点帧复验，绑定当前正式选图SHA；不等同于客户端验收。
- [收尾记录](provenance/foot-axis-20261004/closeout.json)由[收尾脚本](tools/closeout-axis-run.py)在验收、17张提升和浏览器SHA全部核实后生成；[最终文件核验](provenance/final-validation.json)继续保留。
- [本轮清理记录](provenance/foot-axis-20261004/cleanup.json)：在成品与引用完整核验后清理原生、拒稿和中间图，记录实际删除结果，保留逐图来源文字。

旧离线验收和旧选表保留历史SHA；本轮以当前正式清单、对应验收和成功收尾记录为准。预览只读正式文件，不依赖清理后的原生或诊断图。其他角色、客户端和全局设置不在本次修改范围。接入时仍需按实际相机和世界移动速度复核脚滑与观感。

2026-10-05时长更正：当前跑步为60ms/帧、16帧共960ms，每两帧接地位置占120ms。当前配置与预览已同步，历史验收中的75ms/1200ms只记录当时状态，见[时长更正记录](provenance/timing-60ms-20261005/change.json)。
