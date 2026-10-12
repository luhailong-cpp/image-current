# 本批模型目标核对

2026-10-05 实际打开官方发布与模型文档：

- https://openai.com/index/introducing-chatgpt-images-2-5/ ：ChatGPT Images 2.5 已提供给 ChatGPT、ChatGPT Work 和 Codex。
- https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst ：Sunburst 被列为最强图像生成/编辑型号，quality 包括 low、medium、high、xhigh、max、auto。

沿用用户指定目标 gpt-image-2.5-sunburst / max，公共配置只读。本次内置工具只允许 prompt、referenced_image_paths、num_last_images_to_include、transparent_background，没有 model/quality 选择器；返回 image_url 和 output_hint。逐图 actualModel、actualQuality 与 submittedParameters 的对应字段为 null，不把公告或提示词当作模型锁定证据。
