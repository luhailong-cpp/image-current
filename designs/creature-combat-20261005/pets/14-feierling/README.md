# 绯耳灵 · 三种战斗动作

**已完成68张正式1024×1024透明RGBA PNG。** E为斜前朝右下，W为独立绘制的真正斜后朝左上；左手持雕木狐面具，右手掌击/结诀，保留铜红短发、两狐耳、单条黑尖红尾与深玉象牙丝衣。

|动作|每向帧数|每帧时长|单向总时长|
|---|---:|---:|---:|
|受击 hit|6|40ms|240ms|
|普攻 attack|12|30ms|360ms|
|施法 cast|16|45ms|720ms|

[打开六组动作预览](preview.html)：正常速度、0.25慢放、逐帧滑杆/按钮与锚点开关。预览只读取本目录runtime，可在普通浏览器打开本地HTML；全部图片载入后开始计时。[六组代表帧](QA/overview.png)可快速查看方向与动作。

正式资源位于runtime/<hit|attack|cast>/<E|W>/NN.png；读取[manifest.json](manifest.json)取得全部路径、时长、pivot、事件、来源和视觉状态，[SHA256SUMS.txt](SHA256SUMS.txt)校验PNG。

名义脚点[512,942]（顶部原点），pivot[0.5,0.08]（左下原点）。实际原生1254×1254整幅缩至853×853；E偏移[0,126]，W偏移[50,126]，同方向跨三动作一致，不裁主体、不逐帧重新对脚。见[固定导出记录](EXPORT_TRANSFORMS.json)。双足随反冲/屈膝在名义根点周围自然移动。

已逐张查看全部帧并检查六组正常、慢放与逐帧预览，修正了换侧、击发方向、收势灵光和末段体型跳动。见[技术检查](QA/technical-validation.json)、[视觉检查](QA/visual-review.json)、[清理后验证](QA/final-validation.json)。这些属于素材与本地预览检查；**尚未接入客户端或进行游戏内验收**。

逐图prompt、附图角色、时间、配置快照、工具回执、原生SHA与导出SHA保存在generation/<action>/<direction>/NN.generation.json及旁边文字文件。配置目标GPT Image2.5/max（gpt-image-2.5-sunburst）；内置工具无model/quality选择器，实际提交对应字段和actualModel/actualQuality均为null，宿主未披露。见[模型目标核对](MODEL_VERIFICATION.md)。

已按项目规则清理本目录原生、拒稿及加工中间图片，不留图片备份；保留来源文字和SHA，历史来源路径不再是播放依赖。共享身份/风格原图未删除。[清理记录](QA/cleanup.json)、[状态](STATUS.md)、[接入交接](MERGE_HANDOFF.md)、[姿态设计](POSES.md)均随包保留。build_delivery.py可用正式PNG重建清单和预览；finalize_export.py仅记录生成阶段导出方式，清理后不保证能恢复已删原生像素。
