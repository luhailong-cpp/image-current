# 本批目标与工具证据

2026-10-05 已检索并打开 [官方 GPT Image 2.5 Sunburst 模型页](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)，页面列有 max 质量。本批沿用用户明确选择及配置快照 gpt-image-2.5-sunburst / max，不改共享配置。

本次内置 image_gen.imagegen 仅开放 prompt、referenced_image_paths / num_last_images_to_include、transparent_background，未提供 model 或 quality 选择器。各实际提交 model/quality、返回 actualModel/actualQuality 均按证据记 null；文档、提示词与配置目标不代表实际模型确认。

本地后处理只做全画布固定缩放和透明留边、预览与检查，不生成或插补姿态。无 API/CLI 付费调用。
