> 2026-09-25：用户明确要求本游戏原创地名与美术，本稿沿用外部游戏地名的方案已被替换。请使用[新版《五行奇谈》原创山海舆图](../world-map-original-20260925/README.md)。下文与图像仅保留历史来源记录。

# 选择场景 · 山海世界地图

按本次用户提供的世界地图截图重新绘制，沿用 designs 已确认的道家 Q 版高清手绘风格。保留山海地貌、场景地名、天墉城当前位置及“练功区／去天界”入口，界面使用玉绿、象牙米白、暖金和少量花灯点缀。

- [2560 × 1080 展示图](world-map_2560x1080.png)：从原图高质量重采样，非原生 2560 生成。
- [原生生成图](world-map.png)：1931 × 814 PNG，原始文件和内嵌来源元数据完整保留。
- [原图版本与质量记录](world-map.png.generation.json)。
- [展示图派生记录](world-map_2560x1080.png.generation.json)。
- [实际提示词](source/world-map.prompt.txt)。
- [工具调用记录](source/tool-receipt.json)与[配置快照](source/config-snapshot.json)。
- [主要风格样板](../guild-ui-v2/source/guild-overview.png)；[用户功能参考图](source/reference-function-world-map.jpg)。

用户指定优先 GPT Image 2.5，无法使用时退至 2.0。2026-09-24 核对[官方新版公告](https://openai.com/index/introducing-chatgpt-images-2-5/)，Images 2.5 已向 Codex 开放，因此使用已授权的内置生图入口，配置目标为 Images 2.5 / gpt-image-2.5-sunburst / max。

本工具没有 model 或 quality 选择器。结果未披露具体版本；原图内嵌来源信息仅为 ChatGPT / gpt-image，因此实际是 2.5 还是 2.0、具体分支及质量档位均未确认。未使用付费 API/CLI。官方开放公告、配置目标、实际提交参数与结果证据分别记录。

图片查看的默认通道遇到 Windows 沙盒初始化错误。使用只读加载的 1200 像素宽内存预览展示项目风格样板，再通过对话图像输入提交两张参考图；用户截图仅用于功能与布局。

本次交付为静态视觉稿。地图标签按功能截图保留；无需把这里视为已接入客户端的可点击地图或可行走场景。项目旧的线路选择稿保持原样。
