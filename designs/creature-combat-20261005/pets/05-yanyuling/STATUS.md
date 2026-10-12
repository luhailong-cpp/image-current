# 砚羽灵制作状态

完成：2026-10-05。正式美术资源和预览已交付；游戏接入未验证。

|项目|状态|
|---|---|
|受击 E / W|各6帧，40ms/帧，完成|
|普攻 E / W|各12帧，30ms/帧，完成|
|施法 E / W|各16帧，45ms/帧，完成|
|正式输出|68张独立姿态，1024×1024 RGBA透明PNG|
|技术验收|尺寸、alpha、SHA、来源引用、缺帧、重复像素检查通过|
|美术检查|全68帧及六组正常／0.25倍连播已检查，末轮修正attack E07/E11与cast W12|
|预览|互动逐帧页面＋六组正常／慢放APNG共12份|
|来源记录|逐图prompt、receipt、目标与实际参数、原生SHA、导出链齐全|
|素材清理|项目内被替代的中间图片删除，历史文字和SHA保留，详见cleanup.json|
|游戏接入|未读取或修改客户端；尚未验证引擎播放与战斗逻辑|

以[manifest.json](manifest.json)、[技术验收](qa/technical-validation.json)、[最终美术验收](qa/visual-review-final.json)和[SHA清单](CHECKSUMS.sha256)为准。[README](README.md)提供查看方式、时长及锚点说明。[接手说明](MERGE_HANDOFF.md)保留接入边界。

模型目标为GPT Image2.5 Sunburst／max；内置入口未披露实际型号和质量，实际记录均为null。固定导出基准有人工估计误差，未通过逐帧移动伪造动作或锁死自然反冲。
