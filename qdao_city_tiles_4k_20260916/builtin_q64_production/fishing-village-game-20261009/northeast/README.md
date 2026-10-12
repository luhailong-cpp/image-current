# 渔村东北区正式资源制作记录

本目录负责 `r01–r07 / c08–c14` 共 49 块，首块为 `r06_c12`。**尚无验收通过的正式 4K 图块，49 块任务未完成。** 数量与断点以 [progress.json](progress.json) 为准。

## 坐标与生成方式

- 共享制作契约为上级 `production-contract.json`。本区不修改该契约、全局生图配置或客户端。
- 首块全局范围为 `[45056,20480,49152,24576)`，按 4×4 个原生核心制作。每个原生结果实测 1254×1254；核心裁切为 `[115,115,1139,1139)`，相邻原生画面共有 230 像素重叠。
- 最终候选只允许整数裁切与不透明拼接；总览放大图仅作为构图引导，不进入成品像素。机械桥接候选不计为新的 AI 生成次数。
- 使用宿主内置 `image_gen`，未使用付费 API。配置目标是 `gpt-image-2.5-sunburst / max`；工具没有型号和质量参数，返回值也未披露实际型号或质量，因此二者均标记为**未确认**。
- 每次生成的 prompt、实际参考顺序、调用回执、原生尺寸、哈希和来源记录分别保存在 `records/` 与 `native/*.generation.json`。机械衍生图以 `*.derived.json` 追溯原图。

## 当前检验重点

首块已经由 16 个原生核心完整覆盖并导出 4096×4096 候选。当前累计 36 次原生生成；首块及其余 48 块均未完成正式验收。`p13/p14` 石板接缝、`p22/p23` 鱼摊前沿已做联合修复，中央几何改善，但全图检查仍发现四片交点木梁错位、部分桥接外缘的笔触/色调跳变和材质偏离。局部接缝通过不等于整片或整块通过。

明确选片表为 [records/r06_c12.selection.json](records/r06_c12.selection.json)。`assemble_candidate.py` 在 16 片和来源记录齐全后生成 `tiles/r06_c12.candidate.png`、24 条全长原生边界、9 个四片交点及预览图；其所有验收标志保持 false。`export_core_review.py` 再导出 16 张不缩放核心图，用于检查片内断线。

联修结果必须同时检查中央接缝、左右外接边及上下外接边。修复一条接缝却破坏相邻接缝的候选不能采用。候选数量不得记入 `complete4kCount` 或 `formalAcceptedCount`。

已经完成的检查与当前候选：

- [4096×4096 候选，未验收](tiles/r06_c12.candidate.png)
- [仅用于预览的 1024 缩略图](qa/r06_c12/r06_c12.preview-only-1024.png)
- [机械覆盖与来源清单](qa/r06_c12/manifest.json)
- [上半 8 核心与 6 竖缝](qa/r06_c12/upper-core-review.json)
- [下半 8 核心与 6 竖缝](qa/r06_c12/lower-core-review.json)
- [12 横缝与 9 个交点](qa/r06_c12/horizontal-junction-review.json)
- [明确的四片交点木梁阶差](qa/r06_c12/junction_r2_c2.native-1to1.png)
- [材质偏差原尺寸观察](qa/root-material-observations.json)

本轮两次针对性修复均未通过，当前断点与接续条件见 [BLOCKERS.md](BLOCKERS.md)。未通过的边缘不扩展为其他 4K 图块。以当前候选哈希匹配各份 QA；后续候选变化后，受影响的旧 QA 不能自动沿用。

## 记录与接续

- [全部区块计划](records/zone-tile-plan.json)
- [首块精确坐标](records/r06_c12.coordinates.json)
- [官方型号核对记录](records/model-verification-20261009.json)
- [来源元数据修正记录](records/provenance-metadata-corrections.json)
- [来源审计快照](records/provenance-audit-final.json)（审计范围与排除项见文件，后续生成不自动视为已审计）

外侧相邻 4K 图块及跨区连接尚未检验；客户端映射、导航和 5000 人容量均未验证。当前图片为尚未通过验收的在制稿及其来源证据，不接入正式游戏资源索引。成品通过、当前引用完整后，再依项目素材保留规则清理原图、拒稿及加工中间图；不在本阶段删除共享参考图。
