# 游戏地图素材

换电脑请先看 [迁移交接](docs/COMPUTER_HANDOFF_20261011.md)。2026-10-12 用户要求“边继续做边传吧”，上传窗口已确认本批内容固定为独立快照，现按[最新恢复指令](docs/MAP_PRODUCTION_RESUME_20261012.json)恢复主城、渔村和八仙岛制作。15/15 [迁移冻结记录](MAP_MIGRATION_FREEZE_20261011.json)及各区断点保留为已捕获批次的历史证据；新增图另批补传，不能把本地存在或旧冻结就绪当作新图已上传。

## 给接手的 Codex

2026-10-10 根据当前用户要求与在制记录恢复本交接入口。先读 [已确认风格](designs/README.md)、[统一配置](config/image-generation.json)、[逐图策略](docs/IMAGE_MODEL_POLICY.md)、[UI 视觉](qdao_ui_redesign_v5/UI_SPEC.md)，再读 [当前恢复制作指令](qdao_city_tiles_4k_20260916/builtin_q64_production/resume-production-20261010/README.md)。

当前仅主城、渔村、八仙岛三张日景；各自 production-contract.json 定义固定绘图坐标与分区。主城 16×16 个 4096 图块；渔村和岛各 14×14。三图均未完成。5000 人静态脚点排布已通过条件试验；用户已明确本任务只做地图美术，实际游戏运行不在制作范围。现在从当前采用版本和缺片断点继续，保留全部原图和中间稿，不回填旧图片的模型字段。提交和上传仍由上传窗口统一处理。
