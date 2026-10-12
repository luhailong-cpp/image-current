# 选择场景 · 线路选择视觉稿

按用户提供的线路选择截图重绘，沿用 designs 已确认的手绘玉绿、象牙米白、暖金道家 Q 版风格。三列八行共 24 项，七线至三十线；三十线显示当前状态，底部保留取消和确认。

- [成图](scene-select.png)：原生 1931 × 814 PNG，未放大。
- [逐图版本与质量记录](scene-select.png.generation.json)。
- [实际提示词](source/scene-select.prompt.txt)。
- [内置工具调用记录](source/tool-receipt.json)。
- [配置快照](source/config-snapshot.json)。
- [主要风格参考](../team-ui-v2/team-ui-v2.png)；[用户功能截图](source/reference-function-lines.jpg)。

本次使用内置 image_gen。目标为配置中的 Images 2.5 / gpt-image-2.5-sunburst / max；官方已宣布向 Codex 开放，但本工具不提供模型或质量选择器。返回值未披露版本；原图内嵌来源元数据仅标识 ChatGPT / gpt-image，**实际为 2.5 还是 2.0、具体分支和质量档位均未确认**。不将目标配置当作实际调用参数。

文件路径参考图通道受当前沙箱初始化故障影响，首次调用未产图；成功调用使用已载入对话的两张参考图片。风格参考为原图的 1536 宽内存查看预览；截图仅用于功能。保留原生输出及其内嵌来源元数据。

视觉检查：24 个线路名称及排列正确，当前标记、标题、关闭、取消与确认完整可读；画法与已确认样板一致。此交付为静态整屏视觉稿。

官方核对（2026-09-24）：[Images 2.5 发布公告](https://openai.com/index/introducing-chatgpt-images-2-5/) · [图像生成文档](https://developers.openai.com/api/docs/guides/image-generation)。
