# 玄潮龟 · hit W 制作状态

2026-10-05。W 向受击 6 张独立内置 AI 帧已完成，40ms／帧，共 240ms；未制作移动动作。

- 正式图：`runtime/hit/W/01.png` 至 `06.png`，均为 1024×1024 RGBA。
- 准确提示词：`prompts/hit/W/NN.txt`；逐图 sidecar：`runtime/hit/W/NN.png.generation.json`；原生生成记录与回执：`provenance/hit/W/NN.generation.json`、`NN.receipt.json`。
- 每次实际附 TASK 的原生 E／W 身份与主要画法参考，另附前帧／施法 W01 作为真实同向动作和构图参考。已逐张实际看返回图。
- 采用受力起始、缩颈压缩、峰值、半回弹、缓冲、警戒回位六阶段，真实 W 斜后朝左上；后脑、背甲与两后足可见。四足／三爪、右侧桂枝朱结玉珠短穗、单尾和盂内月牙保持原有身份。
- 原生均为 1254×1254，统一整画布等比缩至 1024。没有主体裁切、贴底、整体平移、镜像、复制或插值补帧。
- 通过内置 `image_gen.imagegen` 生成，沿用 `gpt-image-2.5-sunburst` / `max` 目标；实际 model／quality 提交参数与返回未披露，按真实证据记 `null`。

W04 首稿反弹颈部过度伸展，已真实 AI 定点修正；未采用稿的完整 prompt、receipt、generation 文字证据保存在 `provenance/hit/W/04-rejected-overextended.*`，交付目录没有拒稿图片副本。共 7 次成功返回图，采用 6 张。本向没有网络失败。

[`provenance/hit/W/technical-check.json`](provenance/hit/W/technical-check.json) 检查为 6／6、0 错误、无精确重复，尺寸／RGBA／SHA／透明背景及来源链、prompt 和参考路径均检查完成。6 张边界提示的最大 alpha：W03 为 6，其余均 1；所有帧边缘 alpha≥16 像素数为 0。未为消除警告修改原生透明像素。

此处记录逐张原生图目视与技术结果。正常／0.25 慢放中的连续性、脚爪支撑与首尾衔接还需要整组实际预览；不宣称动态或客户端验收通过。客户端未接入。

没有改动根公共清单、其它角色或 Git 状态。原生输出仍由宿主默认生成目录管理，最终清理与引用完整性由主任务统一处理。
