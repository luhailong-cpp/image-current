# 符小虎 · 两向战斗动作

只使用 Image 原有「符小虎」身份制作。68张正式动作帧已完成并通过本包技术、来源与视觉检查，完整状态见 [STATUS.md](STATUS.md)。

|动作|E斜前朝右下|W真正斜后朝左上|每帧时间|单向时长|
|---|---:|---:|---:|---:|
|受击 hit|6|6|40ms|240ms|
|普攻 attack|12|12|30ms|360ms|
|施法 cast|16|16|45ms|720ms|

正式合同为68张1024×1024 RGBA PNG。坐姿、杏金虎纹、额前黄符、胸前太极铃、绿金披肩、四肢及一条粗短弯尾沿用原图；W独立绘制，额符与铃随正背遮挡，不转贴背后。本包不含走路、跑步或移动循环。

## 打开与使用

- 完整交付包：`delivery/fu-xiao-hu-combat-68frames.zip`；解压后打开`fu-xiao-hu-combat/preview/index.html`。压缩包外附SHA256与打包核验记录，包含正式帧、预览、manifest和逐图来源文字。
- [六组总预览](preview/index.html)：正常1×、0.25×慢放、逐帧滑条、前后帧与深浅底。
- [受击E](preview/hit-E.html) · [受击W](preview/hit-W.html) · [普攻E](preview/attack-E.html) · [普攻W](preview/attack-W.html) · [施法E](preview/cast-E.html) · [施法W](preview/cast-W.html)。各页含正常/慢放WebP与逐帧总览链接。
- 正式路径为 `runtime/<hit|attack|cast>/<E|W>/01.png` 起连续编号；[manifest.json](manifest.json) 含每帧尺寸、时间、逻辑脚点、事件建议、SHA及来源。
- [POSES.md](POSES.md) 锁定解剖左右与姿态阶段。[design/E-reference.png](design/E-reference.png) 与 [design/W-reference.png](design/W-reference.png) 是当前有效方向参考。

脚点顶部原点[512,942]、底部归一pivot[0.5,0.08]。原生工具返回1254×1254，统一整画布LANCZOS导出1024；最终E固定偏移[0,-15]、W[0,-4]，同向所有动作共用一个变换。没有逐帧以脚底重新对齐，没有镜像、复制、全图平移或插值制作缺帧。统一导出变换本身不生成动作。

## 来源与质量证据

全部创作与定点修图使用宿主内置 `image_gen`，每次生成一个独立姿态。用户目标配置为 `gpt-image-2.5-sunburst / max`（ChatGPT Images2.5）。工具未暴露model/quality参数且未返回可核实值，实际型号/质量均为未确认/null；没有走收费API/CLI。官方目标核对见 [records/model-verification.md](records/model-verification.md)。

逐图索引为 [records/source-audit.json](records/source-audit.json)，对应manifest各行的sourceRecord、实际prompt/request、receipt、当次配置快照、原生SHA与导出链。旧候选记录保留文字证据，不把配置目标当作实际API选择器。原图/在制稿按最终引用核验后清理，当前方向设计保留；跨窗口原宠和风格参考没有删除。

技术结果见 [validation.json](validation.json)，视觉检查见 [records/visual-review.json](records/visual-review.json)，12个动画预览的帧数与时长见 [records/preview-audit.json](records/preview-audit.json)。逐帧绘制保留轻微毛纹与轮廓变化，正常/慢放、触击/释放及末帧回首帧均已检查。帧文件与预览不等于客户端接入通过；未访问或接入客户端，未提交、推送、修改分支或索引。后续交接见 [MERGE_HANDOFF.md](MERGE_HANDOFF.md)。

## 本地检查工具

`tools/build_delivery.py` 由现有真实帧重新生成manifest与预览；`tools/audit_sources.py` 检查逐图来源链与SHA；`tools/calibrate_export.py` 只做一次按方向固定导出校准。工具不调用付费API，不创作缺失姿态。Python需要Pillow，浏览器可直接打开preview内HTML；如浏览器限制本地路径可在本目录运行 `python -m http.server`。
