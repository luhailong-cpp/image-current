# 本批目标与实际入口证据

本批沿用用户明确的 GPT Image 2.5 / max 目标。配置快照逐图保存，不修改公共配置或旧图记录。

2026-10-05 使用官方文档核对 [GPT Image 2.5 Sunburst 模型页](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)：页内列有 gpt-image-2.5-sunburst 与 dated snapshot，支持 max 质量。本批工具并未开放 model / quality 参数；官方模型页不能作为本次实际模型版本或质量的证明。

本批均使用内置 image_gen.imagegen，实际提交字段为 prompt、referenced_image_paths、transparent_background=true。工具结果仅返回 image_url 和 output_hint。实际 submittedParameters.model / quality 及 actualModel / actualQuality 均为 null。没有调用付费API/CLI。

逐图证据索引：records/{hit|attack|cast}/{E|W}/{NN}.generation.json。每条记录关联实际提示词、原有E/W身份图、主要画法样板、工具结果回执、原生尺寸和源SHA。定点重试的旧来源文字继续保留；被清理的源图在相应记录与清理单中标记，未知模型值不会因目标配置而回填。
