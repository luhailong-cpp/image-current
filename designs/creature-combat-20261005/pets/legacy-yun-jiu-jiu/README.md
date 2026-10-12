# 云啾啾 · 双向战斗动作

2026-10-05。沿用 Image 原有白羽红冠幼鹤「云啾啾」，交付68张1024×1024 RGBA独立帧。E为斜正面朝右下，W为独立绘制的斜背朝左上。

打开 [全部动作预览](preview/index.html)，可正常播放、0.25倍慢放或逐帧检查。六组也可单独打开：

|动作|E正面|W背面|每向时长|
|---|---|---|---|
|受击|[6帧](preview/hit-E.html)|[6帧](preview/hit-W.html)|6×40ms＝240ms|
|普攻|[12帧](preview/attack-E.html)|[12帧](preview/attack-W.html)|12×30ms＝360ms|
|施法|[16帧](preview/cast-E.html)|[16帧](preview/cast-W.html)|16×45ms＝720ms|

正式资源在 `runtime/<hit|attack|cast>/<E|W>/01.png` 起编号。[manifest.json](manifest.json)列出方向、序号、时长、事件、SHA、来源与固定导出变换。脚点为顶左坐标[512,942]，左下pivot为[0.5,0.08]；同方向跨动作统一缩放，不逐帧对脚。原生图1254×1254，整画布缩至928×928后置于1024画布[48,35]，不是原生1024出图。

已完成全部68帧逐图与总览检查，实际运行六组正常／0.25倍浏览器播放并检查逐帧控制。[最终检查记录](qa/final-review.json)区分静态检查、播放采样与技术检查。普攻峰值仍有轻微云垫起伏和轮廓变化，E06–08有头身透视变化；没有用逐帧挪图消除这些原生差异。浏览器采样不是高刷新率测量；未接入客户端，不宣称客户端动画验收通过。

[validation.json](validation.json)记录68/68、尺寸、RGBA、无缺帧、无完全重复／纯平移重复／跨向镜像、来源和SHA检查。真实动作均来自内置image_gen逐帧生成或编辑，没有复制、镜像、插值补帧，也没有移动动画。

逐图来源入口：每张runtime PNG旁的 `.generation.json` → 对应 `records/*.json` → 实际 `prompts/*.txt`。95次成功出图含68选定动作帧、2张当前方向设计及25张未选候选。目标配置为gpt-image-2.5-sunburst/max；内置工具没有model/quality参数，实际提交和实际返回版本／质量为null（宿主管理未披露）。不将提示词、配置或公告当成实际模型证据。[来源审计](qa/provenance-audit.json)保留逐项核对，4条早期记录使用简化回执但保留真实返回路径与源SHA。

原身份仅使用 `D:/work/image/qdao_chibi_pets_v1/03_yun_jiu_jiu-transparent_1254.png`；主要画法参考为 `designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png`。两者均实际查看并附入生图。当前 [E方向设计](source/design-E.png) 与 [W方向设计](source/design-W.png)保留作后续身份参考。

成品与来源核对后，原生动作图、拒稿和过程QA图片按项目规则清理；源SHA、提示词、实际参考与回执继续保留，详见 [cleanup.json](cleanup.json)。来源记录中的旧输入路径属于历史证据，`referenceRetentionAudit`给出可用的正式帧替代路径；不表示旧图仍可读取。原有跨窗口身份／风格图及宿主管理缓存未在本目录清理中操作。

复核现有成品使用：`tools/build_combat.py verify --transforms tools/export-transforms.json`。原生动作图已清理，`export`不能从已删除的原图重新生成像素。见 [工具说明](tools/README.md) 与 [接入交接](MERGE_HANDOFF.md)。
