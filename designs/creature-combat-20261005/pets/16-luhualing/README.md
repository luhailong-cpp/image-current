# 露华灵 · 战斗动作

**已完成素材交付：68 张正式帧，六组动作。本地逐帧与播放检查完成；客户端未接入。** 日期：2026-10-05。沿用原有墨青短发露华女仙、米白青瓷纱袖、紫釉露壶与桂枝露珠，只补受击、普攻、施法。

|动作|每向帧数|每帧时间|E/W合计|
|---|---:|---:|---:|
|hit|6|40ms|12|
|attack|12|30ms|24|
|cast|16|45ms|32|

E为朝右下的斜前视；W为朝左上的真实斜后视。每帧独立AI生成，不镜像、不复制、不插值。成品路径为 `runtime/<action>/<E或W>/NN.png`，1024×1024 RGBA；pivot为左下坐标[0.5,0.08]，顶部原点锚[512,942]。

- [当前状态](STATUS.md)
- [动作姿态合同](POSES.md)
- [正常、慢放与逐帧预览](preview/index.html)
- [帧清单](manifest.json) 与 [技术检查](validation.json)
- [全帧与动态检查记录](visual-review.json)
- [SHA256清单](SHA256SUMS.txt)
- [逐图来源索引](generation-index.json) 与 [来源链检查](provenance-validation.json)
- [模型核对](MODEL_VERIFICATION.json)
- [接入交接](MERGE_HANDOFF.md) 与 [素材清理记录](cleanup.json)

本批采用宿主内置 `image_gen.imagegen`。目标沿配置 GPT Image 2.5 Sunburst / max；实际工具无型号与质量选择器，未返回可核实型号与质量，逐图记为null。官方目标核对见 [OpenAI模型页面](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)，不能用该公告证明每次真实返回型号。

每张原生记录位于 `records/<action>/<direction>/NN.generation.json`，其中链接实际prompt与工具receipt。每张正式PNG旁的 `.png.generation.json` 保存统一缩放导出、原图SHA与原生记录。原生1254×1254整画布统一缩至896×896，贴入1024画布[64,69]，不逐帧调脚点。后处理不冒充新的AI姿态。

已按根素材保留规则清理本目录 72 张原生、拒稿及临时审图图片；保留 68 张正式 PNG、6 张最终联系表、预览和完整文字来源。历史记录中的原生输入路径及 SHA 为生成当时证据，对应图片已删除；当前交付引用使用 runtime。公共身份与画法参考保持只读，未删除。

本地审查查看了每张生成/修复图与最终六张联系表，实际操作六组正常播放、0.25×慢放和逐帧，检查关键帧及收势。已修复发现的道具换手、特效裁边与释放轨迹问题。预览的重复播放便于检查，素材本身是单次动作。未接入客户端，未进行客户端验收。
