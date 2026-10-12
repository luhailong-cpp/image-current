# 霜团貂 · 受击 / 普攻 / 施法

2026-10-08最终素材交付。68张独立AI姿态、1024×1024透明PNG已补齐、修正并完成静态复核。本目录只制作原有霜团貂的三种战斗动作。[完整状态](STATUS.md)。

最终原速视频仅完成播放器截图抽查；最终慢放因播放器窗口退出未完成实看。素材、静态验收与预览编码检查已完成，完整动态与客户端验收尚未完成。

## 查看与接入文件

[正常速度总览视频](preview/video/six-groups-normal.mp4) · [0.25慢放总览视频](preview/video/six-groups-slow.mp4) · [六组逐帧交互预览](preview/index.html)

|动作|E斜前朝右下|W真斜后朝左上|每向规格|
|---|---|---|---|
|受击|[正常](preview/media/hit-E-normal.webp) · [慢放](preview/media/hit-E-slow.webp)|[正常](preview/media/hit-W-normal.webp) · [慢放](preview/media/hit-W-slow.webp)|6帧×40ms，240ms|
|普攻|[正常](preview/media/attack-E-normal.webp) · [慢放](preview/media/attack-E-slow.webp)|[正常](preview/media/attack-W-normal.webp) · [慢放](preview/media/attack-W-slow.webp)|12帧×30ms，360ms|
|施法|[正常](preview/media/cast-E-normal.webp) · [慢放](preview/media/cast-E-slow.webp)|[正常](preview/media/cast-W-normal.webp) · [慢放](preview/media/cast-W-slow.webp)|16帧×45ms，720ms|

正式图片位于 `runtime/{hit|attack|cast}/{E|W}/{NN}.png`。WebP与MP4是带浅底的查看文件；交互预览支持暂停、原时长、0.25慢放和逐帧定位。各预览只依序显示既有正式帧，无插值造帧。

[manifest](manifest.json) · [SHA256](SHA256SUMS.txt) · [技术检查](validation.json) · [像素与Alpha](qa/pixel-alpha-audit.json) · [动画编码与来源检查](qa/animation-encoding.json)

## 身份、导出和事件

沿用Image原有珠灰圆耳灵貂：琥珀眼、四足、浅玉宽卷单尾、象牙青瓷丝巾、月玉露坠和花饰。生成与编辑实际附原有E/W身份图及指定手绘风格参考。

E为斜前朝右下；W独立绘制真正斜后朝左上。全帧使用同一整画布1254→1024等比导出，保留画内重心变化。顶部原点锚点为 `[512,942]`；左下归一pivot为 `[0.5,0.08]`。没有逐帧脚点重定位、镜像、复制、插值或移动循环。

[POSES](POSES.md)记录解剖归属和阶段。普攻08帧为 `attack-contact`，施法11帧为 `cast-release`。动作按单次事件播放；预览循环用于检查收势。

## 当前验收证据

验收必须匹配正式图片当前SHA；旧来源和旧验收文字保留历史用途，不能套用到修后像素。

- [受击与普攻36帧独立静态复核](qa/attack/final-static-review-20261008.md)
- [普攻W10–12后足修正](qa/attack/repair-20261008-accepted.md)
- [施法E最终16帧静态复核](qa/cast/repair-E-20261008/final-static-review.md)
- [施法W最终16帧静态复核与修复](qa/cast/repair-W-20261008/review.md)
- [68帧当前SHA与静态验收总表](qa/final-visual-review.json)
- [播放实看状态与覆盖范围](qa/playback-status.json)

技术检查只核对文件、透明、尺寸、重复、引用与SHA。连续播放的实际观察范围单独记录；客户端未读取、未接入、未验收。

## 模型与素材保留

[逐图来源索引](generation-index.md) · [官方目标核对与工具证据](qa/model-evidence.md)

使用内置 `image_gen`，配置目标 `gpt-image-2.5-sunburst/max`。工具没有暴露型号/质量选择器或真实返回值，实际提交与实际型号/质量均按未知记为 `null`，不把提示词或目标配置当作已锁定型号。逐图保留提示词、参考来源、回执、原生尺寸和SHA；未使用付费API/CLI。

按项目规则，最终输出和引用确认后清理本目录原生图、拒稿、回退和加工中间图，保留文字来源与最终资源。公共身份/风格参考和范围外宿主缓存不动。

## 重新构建

按顺序运行 `tools/build_media.py`、`tools/build_video_preview.py`、`tools/audit_pixels.py`、`tools/verify_previews.py`、`tools/build_delivery.py --strict`。素材预览需要Pillow，视频另需 `imageio-ffmpeg==0.6.0`；清单构建只用Python标准库。脚本不会创造缺失姿态。

[交接说明](MERGE_HANDOFF.md) · [状态](STATUS.md)
