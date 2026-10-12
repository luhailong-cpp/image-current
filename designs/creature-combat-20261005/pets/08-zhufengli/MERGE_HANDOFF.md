# 竹风狸素材接手

本目录是唯一可写工作范围，不涉及 Git 合并操作。未提交、推送、切分支或改Git索引。

2026-10-08 完成68帧素材交付。`qa/technical.json` 为pass；`qa/visual-review.json` 为reviewed-with-notes，六组正常与0.25慢放已查看，无阻断问题。少量毛丝、叶缘和支撑点变化详见视觉记录；`manifest.json` 内 deliveryComplete 与逐帧视觉状态仅对应记录的SHA。

使用 `manifest.json` 的 `runtime/<action>/<direction>/<frame>.png`、durationMs、pivot、anchorTopLeft与event。保持1024完整透明画布，禁止按每帧bbox重居中；E敌方斜前右下、W我方斜后左上。hit/attack/cast均为原地动作，接入代码不得把本包当走路或跑步序列。

当前验收以清单 `visualReviewSHA256` 及每帧 `visualReview` 为索引，后者包含报告路径/校验值、JSON Pointer和正式图SHA。应同时匹配报告 `frameSnapshot` 与实际PNG，不能仅凭状态字符串判断。`DOCUMENT_SHA256SUMS.txt` 校验当前包内文字文件；`SHA256SUMS.txt` 校验68张正式PNG。生成时的历史检查文字保持原状，以当前总清单和最终报告判定交付状态。

原有跨窗口身份/画法参考位于 Image 项目内部，只读保留。逐图模型目标与未知实际参数见各图generation记录；图片成品无需宿主缓存路径也能播放，宿主原生源SHA只是历史来源证据。

直接打开 `preview/index.html` 可正常/0.25慢放与逐帧；也可查看 `preview/*-1x.png`、`preview/*-025x.png` 动画及 `preview/*-contact.jpg` 全帧图。完整包需保留runtime、manifest/SHA、POSES、prompts、receipts、qa文字记录和preview；无需读取客户端或宿主缓存。包内旧QA图到正式预览的映射见 `qa/cleanup.json`，历史审阅报告中的旧路径按该表查询。

本次没有访问或接入客户端。后续客户端任务应独立验证pivot显示位置、动作结束衔接、事件触发、纹理导入alpha与排序；不得声称本包已通过引擎验收。
