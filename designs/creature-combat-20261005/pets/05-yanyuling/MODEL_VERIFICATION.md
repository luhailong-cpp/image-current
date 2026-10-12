# 本批模型目标与核对证据

核对日期：2026-10-05（America/New_York）。用户显式目标与本批快照：`gpt-image-2.5-sunburst` / `max`，产品目标 ChatGPT Images 2.5。

已打开 [OpenAI发布公告](https://openai.com/index/introducing-chatgpt-images-2-5/)：2026-09-08发布，注明面向ChatGPT、ChatGPT Work和Codex开放。

已打开 [Sunburst模型说明](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)：质量档列为low/medium/high/xhigh/max/auto。核对 [ChatGPT更新说明](https://help.openai.com/en/articles/6825453-chatgpt-release-notes) 与本日官方搜索，未发现需要更换本批目标的新正式图像版本。

本会话内置 `image_gen.imagegen` 仅提供prompt、参考路径和transparent_background等，不提供model/quality选择器。真实调用中没有提交model/quality；逐图记录对应字段为null，actualModel/actualQuality未披露也为null。公告和提示词均不当作已锁定实际参数的证据。未调用付费API/CLI，未改公共配置。

逐图工具结果提示、原生SHA、原生尺寸、提示词与输入参考见provenance及runtime下的.generation.json。生成记录中的UTC时间带Z；用户侧日期按America/New_York理解。
