# 苍嶂麟 W：受击与普攻分组交接

2026-10-05。本组已落盘受击6帧与普攻12帧，共18张独立AI生成1024×1024 RGBA PNG；仅使用内置 image_gen。

- 正式图：`runtime/hit/W/01.png–06.png`，每帧40ms；`runtime/attack/W/01.png–12.png`，每帧30ms，第07帧damage事件。
- 逐图来源：`records/w-hit-attack/{hit|attack}-W-XX.json`；实际提示词在`prompts/w-hit-attack/`。
- 技术检查：`CHECK.json`、`SHA256SUMS.txt`。18帧尺寸、RGBA/alpha、引用、SHA与唯一性通过。
- 统一导出：原生1254方图整幅缩至960×960，贴1024透明画布偏移(32,6)。没有裁切、镜像、插值补帧、整图平移补帧或逐帧对脚。
- 配置目标：gpt-image-2.5-sunburst/max。宿主工具不提供model/quality选择器且未披露实际值；每帧submittedParameters.model/quality、actualModel/actualQuality均为null。

## 已执行的视觉检查

逐张实看18张最终采用帧的工具返回图，另实看三个导出总览：`qa/w-hit-attack/hit-W.png`、`attack-W-01-06.png`、`attack-W-07-12.png`。整体保持后脑、云鬃、玉金背甲、臀部与后蹄的真斜后视，保留四足、两组分叉象牙角与单条云尾，未见前胸翻转、缺肢或多肢、尾数错误、新增翅膀或武器。

受击03可见压低与前甩绢带；普攻03–05低头蓄力、07–08前送顶击、09–12回收。普攻06出现发力抬头后再07低头前送；独立绘制带来的小幅蹄位和装饰变化，需要在总预览正常/0.25慢放下继续判断是否有不自然跳动。未逐帧重对齐来掩盖这类变化。

本子组没有宣称连播已经通过，`CHECK.json`中的dynamicReviewStatus明确保留为待主窗口统一六组连播。客户端接入未执行。

## 定点修正

普攻08首稿头抬得过早，未作为最终图使用。拒稿文字记录为`attack-W-08.attempt-01.json`，对应原提示词在`prompts/w-hit-attack/attack-W-08.attempt-01.txt`。第一次修正请求返回`image generation failed: connection failed: error sending request`，没有输出，原文与输入保存在`attack-W-08.retry-02-error.json`。随后仍通过内置工具重试成功，实际附入普攻07作为第四张姿态连续性参考，得到低头顶击极点；当前`attack-W-08.json`为最终记录。

本组未写公共README、manifest、STATUS或MERGE_HANDOFF，未触碰客户端与Git。项目目录没有生成原图副本；宿主自动落盘路径仍可由每帧source字段追溯，待总资源引用确认后按根素材保留规则统一处理。

2026-10-08：以上为初次分组检查历史。所列旧总览已按素材保留规则清理，当前全帧图在 preview/contact；W attack06 后续已定点修订，最终以 qa/W-final-review.json 和 qa/final-review.json 为准。
