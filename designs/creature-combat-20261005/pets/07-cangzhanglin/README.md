# 苍嶂麟 · 战斗动作成品

完成日期：2026-10-08。沿用 Image 原有苍嶂麟身份，交付 E/W 受击、普攻、施法六组，共 **68 张 1024×1024 RGBA 透明 PNG**。不含移动动作。

打开 [六组交互预览](preview/index.html)：支持原时间正常播放、0.25 倍慢放、暂停、逐帧、独立拖动、背景切换及放大。页面可直接本地打开，不需要联网。

|动作|E 斜前右下|W 真斜后左上|每向帧数 × 时间|总时长|
|---|---|---|---|---|
|受击|[独立预览](preview/hit-E.html) / [全帧图](preview/contact/hit-E.png)|[独立预览](preview/hit-W.html) / [全帧图](preview/contact/hit-W.png)|6 × 40ms|240ms|
|普攻|[独立预览](preview/attack-E.html) / [全帧图](preview/contact/attack-E.png)|[独立预览](preview/attack-W.html) / [全帧图](preview/contact/attack-W.png)|12 × 30ms|360ms|
|施法|[独立预览](preview/cast-E.html) / [全帧图](preview/contact/cast-E.png)|[独立预览](preview/cast-W.html) / [全帧图](preview/contact/cast-W.png)|16 × 45ms|720ms|

## 正式文件与坐标

- 正式资源：`runtime/{hit,attack,cast}/{E,W}/01.png` 起编号。
- [manifest.json](manifest.json)：逐帧方向、动作、尺寸、时间、pivot、事件、SHA、生成记录索引与视觉状态。
- [SHA256SUMS.txt](SHA256SUMS.txt)、[技术检查](validation.json)、[最终视觉复核](qa/final-review.json)、[W 独立复核](qa/W-final-review.json)。
- 原生 AI 输出为 1254×1254，统一整幅缩至 960×960 后置于 1024 方形透明画布的 `(32,6)`；不按每帧最低蹄重新对齐。逻辑落地锚点 top-left `[512,942]`，bottom-left pivot `[0.5,0.08]`。
- 普攻第 07 帧为顶击事件，施法第 10 帧为释放事件。事件为美术接入建议，尚未与战斗逻辑联调。

## 验收结果及边界

68/68 正式帧齐全；尺寸、RGBA/透明通道、文件 SHA、像素重复、提示词/receipt 与原身份/风格引用检查通过。68 帧均已实际查看，六组已在浏览器按正常和 0.25 倍速度播放抽查，并用 16 次全组逐帧操作覆盖各组全部帧。修正了 E 普攻 08 的多余光迹、09 的回收姿态、W 普攻 06 的抬头折返及 W 施法 15 的远侧前蹄可见度。

保留无翼四足、两组自然分叉象牙角、单条云尾及现有玉金鳞甲/薄绢身份；W 始终为真实后侧视角。细甲片、云鬃和薄绢仍有独立手绘帧间细微差异。W 施法 10–11 的气芒比最初提示词更长，已复核朝向、留边与解剖可见性后采用。浏览器观察是播放抽查与逐帧复核，不是连续录像或引擎测试。

**游戏客户端未接入、未验收。** 本任务未读取或修改客户端/兄弟仓库，未执行 Git 提交、推送或切换分支。

## 逐图模型与来源

全部正式帧及修订均由宿主内置 `image_gen` 独立生成或编辑；没有复制、镜像、平移或插值补帧，没有转用付费 API/CLI。`manifest.groups[].frames[].sourceRecord` 是每张正式 PNG 对应的生成记录入口，记录内 `prompt` 指向实际提示词，`evidence` 指向工具返回证据，`references` 说明身份、风格和连续性参考。

本批目标保持 `gpt-image-2.5-sunburst / max`（ChatGPT Images 2.5），配置快照逐图保留。内置工具未提供 `model`/`quality` 选择器，也未返回可核实版本/质量，因此 **submittedParameters.model / quality、actualModel / actualQuality 均为 null，实际未确认**。提示词与官方公告没有被当作实际参数证明。

启动时核对依据：[官方发布公告](https://openai.com/index/introducing-chatgpt-images-2-5/)、[Sunburst 模型说明](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)。10 月 8 日继续的是同一批次，未改写旧图记录。

## 保留与重查

[清理记录](records/cleanup.json)记载已删除的 21 张本目录原生/旧检查图片，保留逐图 SHA、提示词和返回证据。正式 68 帧、当前六张全帧图、预览与交付文档保留。跨窗口原身份/风格图及写入范围外的宿主生成缓存未改动。生成记录中的已退休 `staging` 路径是历史输入证据，正式预览/接入只读 `runtime`。

最终支持的重查入口为 `build_delivery.py`；它不调用生成模型，重新检查正式帧、生成清单和预览。人工视觉复核绑定每张成品 SHA，任何帧变动后不会自动继承旧复核结果。`records` 内的早期分组报告、r1/r2 拒稿文字为历史记录，最终结果以根目录清单和 `qa/final-review.json` 为准。
