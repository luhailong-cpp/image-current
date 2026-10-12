# 玄潮龟交付状态

更新日期：2026-10-08。

最终验收已收口：技术检查 0 错误，全部帧静态检查、六组 1×／0.25× 浏览器播放抽样观察及关键衔接逐帧复核完成。视觉／动态状态为 `pass_with_notes`；42 条极低 alpha 边缘警告保留在报告中，最大边缘 alpha 为 6／255，无 alpha≥16 的像素触边。当前帧 SHA 已绑定人工结论。

受击、攻击、施法的 E／W 六组正式素材均已完成落盘，合计 **68／68 帧**。所有正式图片位于 `runtime`，格式为 1024×1024 RGBA 透明 PNG。

| 范围 | E | W | 制作状态 |
| --- | ---: | ---: | --- |
| 受击 hit | 6 帧 | 6 帧 | 完成 |
| 攻击 attack | 12 帧 | 12 帧 | 完成 |
| 施法 cast | 16 帧 | 16 帧 | 完成 |

最后定点修正已经导出为正式帧：

- `hit/E/04.png`：改为半回弹姿态，衔接受击峰值与后续恢复，避免一帧接近全部抬回。
- `cast/W/06.png`：调整为缓抬的中间姿态，衔接 W05 与 W07。
- `attack/W/12.png`：收势头颈、前足及甲体回到警戒位置，改善末帧至首帧衔接。

18 条攻击原生来源记录的结构已修复；正式导出与原生生成证据分别记录。历史生成输入的 SHA 按当时实际值保存，没有随着参考帧后续返修而改写。具体修正依据见 [hit-E04-final.md](hit-E04-final.md)、[attack-W12-final.md](attack-W12-final.md) 与 [provenance-finalize.md](provenance-finalize.md)。

最终技术结果见 [validation.json](validation.json)，正式文件及 SHA 见 [manifest.json](manifest.json) 和 [SHA256SUMS.txt](SHA256SUMS.txt)。最终人工逐帧、正常速度与 0.25 倍慢放验收以 [visual-review.json](visual-review.json) 为准；素材数量齐全、技术脚本通过与动画视觉通过分别记录。

[六组动作预览](preview/index.html) 已提供正常／慢放／逐帧及透明背景检查功能。**客户端未接入，也未执行引擎内播放、事件或战斗逻辑验收。** 本次工作没有读取客户端或兄弟仓库，没有 Git 提交、推送或索引修改。

本批内置生图目标为 GPT Image 2.5／max；工具未披露实际 model／quality，逐图证据中的实际值为 `null`。交付范围、时序与锚点详见 [README.md](README.md)；接入交接见 [MERGE_HANDOFF.md](MERGE_HANDOFF.md)。
