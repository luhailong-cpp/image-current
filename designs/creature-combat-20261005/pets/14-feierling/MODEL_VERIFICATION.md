# 本批次模型目标核对

2026-10-05 读取项目配置；用户本次明确目标 GPT Image 2.5 / max，内置 image_gen 唯一路径。共享配置只读，快照逐图保存。

已实际打开官方发布页 https://openai.com/index/introducing-chatgpt-images-2-5/ ：页面标注 2026-09-08，说明 Images 2.5 已面向 ChatGPT、ChatGPT Work 与 Codex；API 提供 Flare 与更精细的 Sunburst。

已实际打开官方型号页 https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst ：页面说明 Sunburst 支持 low、medium、high、xhigh、max、auto；明确型号 gpt-image-2.5-sunburst 与快照 gpt-image-2.5-sunburst-2026-09-08。沿用用户指定目标及配置。

本会话内置工具公开参数只有 prompt、referenced_image_paths / num_last_images_to_include 和 transparent_background。没有 model、quality 选择器；实际返回仅 image_url、output_hint。因此实际提交 model/quality 和 actualModel/actualQuality 均为 null，宿主管理未披露。官方产品开放与提示词目标均不代替本次真实路由证据。

未调用付费 API、CLI 或其它图像生成服务。
