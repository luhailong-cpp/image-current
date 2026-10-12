# 本批模型目标核对

核对日期：2026-10-05。用户明确指定 GPT Image 2.5 / max；本批沿用读取到的配置快照，不修改公共配置。

- [OpenAI 发布公告](https://openai.com/index/introducing-chatgpt-images-2-5/)：实际打开页面，2026-09-08发布；公告列明 Images 2.5 面向 ChatGPT、ChatGPT Work、Codex。
- [Sunburst 官方型号说明](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)：实际打开页面并核对支持 low、medium、high、xhigh、max、auto，列明 gpt-image-2.5-sunburst 与 2026-09-08 快照。

当次配置目标为 gpt-image-2.5-sunburst / max。实际入口为 image_gen.imagegen 内置；工具只接受 prompt、referenced_image_paths、transparent_background 等，没有 model 或 quality 选择器。实际提交 model/quality 为 null；工具返回 image_url 与 output_hint，没有实际型号/质量字段。因此每张图 actualModel/actualQuality 均为 null，不能将公告、配置目标或提示词当作本次显式锁定 Sunburst/max 的证明。

图片原生1254×1254，正式导出1024×1024；这是整画布等比Lanczos缩放，不冒称原生1024。未调用API/CLI，无单独计费备用路径。
