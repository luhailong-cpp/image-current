# 霞角鹿 · 受击、普攻、施法

Image 原有霞角鹿的六组战斗素材：可可棕斑点鹿、两枝淡紫杏晶角、四条鹿腿与鹿蹄、一条短尾，无翼；保留紫蓝颈巾、绳结与木坠。沿用原有 E/W 身份与项目画法，只制作原地战斗动作。

正式资源共 **68 张 1024×1024 RGBA 透明 PNG**，位于 [runtime](runtime/)，于 2026-10-08 完成本目录交付。文件、尺寸、alpha、重复、来源引用与 SHA 的最新检查见 [validation.json](validation.json)；全帧静态检查与正常/慢放播放抽查结论独立记录于 [visual-review.json](visual-review.json)，交付状态见 [STATUS.md](STATUS.md)。美术结论为 `accepted-with-notes`：W 受击 04→05 回位偏快，保留节奏备注；客户端状态为 `not-tested`。

## 查看与接入入口

- [交互预览：正常速度、0.25 倍慢放、暂停及逐帧](preview/index.html)
- [manifest：六组帧序、时长、锚点、事件、SHA 与来源](manifest.json)
- [SHA256SUMS：68 张正式 PNG](SHA256SUMS.txt)
- [接入交接](MERGE_HANDOFF.md) · [姿态与解剖锁定](POSES.md) · [任务边界](TASK.md)
- [最终交付审计](provenance/final-delivery-audit.json) · [清理证据](cleanup.json) · [前期逐图来源审计](provenance/audit-final.json) · [提示词](prompts/) · [生成与导出证据](provenance/)

| 动作 | 每向帧数 | 单帧时间 | 单向总时间 | E 预览 | W 预览 |
|---|---:|---:|---:|---|---|
| hit 受击 | 6 | 40 ms | 240 ms | [正常](preview/hit-E-normal.png) / [慢放](preview/hit-E-slow.png) / [总览](preview/hit-E-contact.jpg) | [正常](preview/hit-W-normal.png) / [慢放](preview/hit-W-slow.png) / [总览](preview/hit-W-contact.jpg) |
| attack 普攻 | 12 | 30 ms | 360 ms | [正常](preview/attack-E-normal.png) / [慢放](preview/attack-E-slow.png) / [总览](preview/attack-E-contact.jpg) | [正常](preview/attack-W-normal.png) / [慢放](preview/attack-W-slow.png) / [总览](preview/attack-W-contact.jpg) |
| cast 施法 | 16 | 45 ms | 720 ms | [正常](preview/cast-E-normal.png) / [慢放](preview/cast-E-slow.png) / [总览](preview/cast-E-contact.jpg) | [正常](preview/cast-W-normal.png) / [慢放](preview/cast-W-slow.png) / [总览](preview/cast-W-contact.jpg) |

正常与慢放文件为 APNG，慢放每帧时间为原时间的 4 倍。六组共 12 个动画预览；使用支持 APNG 的查看器播放。交互页面另提供组别切换、逐帧滑块、棋盘格/深色/白色背景及脚点显示。预览循环仅供复核，战斗动作的触发与结束由接入方控制。

## 帧和坐标

正式路径为 `runtime/<hit|attack|cast>/<E|W>/<两位帧号>.png`，各组从 `01` 开始。E 是斜前朝右下；W 是独立绘制的真正斜后朝左上。

原生生成画布为 1254×1254；导出对完整方形画布统一使用 LANCZOS 缩放至 1024×1024。没有逐帧裁切、整图平移、镜像、插值补帧或按最低蹄重新对齐。顶部原点脚点约为 `[512,942]`，左下原点归一化 pivot 为 `[0.5,0.08]`。自然屈膝、反冲、抬肢和回位留在画内。

`manifest.json` 的 `groups` 给出动作、方向、帧数、单帧与总时长及预览路径；`frames` 给出每帧文件、尺寸、事件、pivot、SHA、alpha 和来源。`generationRecord` 指向生成证据，`exportRecord` 指向原生图到正式图的导出证据，`prompt` 指向该帧实际提示词。`visualStatus` 与 `clientIntegration` 独立于 `technicalStatus`。

## 模型与来源证据

本批目标为 `gpt-image-2.5-sunburst / max`，经宿主内置 `image_gen.imagegen` 生成或定点编辑。工具没有 model/quality 选择器，且返回未披露实际型号或质量，因此 `submittedParameters.model`、`submittedParameters.quality`、`actualModel`、`actualQuality` 为 `null`。目标配置不等于已显式锁定的实际模型。

每帧 `provenance/<action>/<direction>/<nn>.json` 保存配置快照、实际提交参数、引用图路径与 SHA、时间、原生尺寸、原生 SHA、提示词路径、工具 receipt 和可得输出证据；对应 `.receipt.json` 留存工具返回记录。`provenance/export/...` 保存正式 PNG 的 SHA、原生来源 SHA 与完整导出操作。修正与拒稿保留文字证据，便于分辨历史版本。时间证据的限制见来源审计，不用未记录的时间补成精确事实。

素材清理遵循根 AGENTS：正式图及引用验证后，删除本目录中已导出的原生图、拒稿、回退和加工中间图片；保留正式资源、必要预览、设计与来源文字。共享身份 E/W 和主风格参考是仍在使用的设计，不在本任务删除范围。历史来源路径可能不再有图像文件，其 SHA 与 receipt 作为来源证据保留。

## 复验与预览重建

本目录的 [build_delivery.py](build_delivery.py) 使用 Python 与 Pillow。原生图保留期间可统一重新导出；清理后使用：

```text
python build_delivery.py --allow-removed-sources
```

清理后的命令验证已保留 `runtime` 与导出记录的 SHA，并从正式帧重建 manifest、校验结果和预览。它不能恢复已删除的 AI 原生图，也不能重新证明被删源文件的当前内容；原生来源以清理前审计、SHA、receipt 和导出记录为证。视觉判断仍须实际逐帧及连播查看。

本包没有移动循环；本任务没有读取或接入客户端，也没有提交、推送、切换分支或修改 Git 共享状态。
