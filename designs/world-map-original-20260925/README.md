# 五行奇谈 · 原创山海舆图

2026-09-25 根据用户“按照我们的游戏命名地图，不要照搬问道的风格和名称”重新原创绘制。本版取代 [上一版场景地图](../world-map-scene-select-20260924/README.md) 的使用位置；旧图与历史生成记录保留作来源档案。

本次重绘采用《五行奇谈》的五行主题，以环水主城“归元城”为中心，组织金西、木东、水北、火南、土中的地域关系。大陆轮廓、河网、主城结构和区域地标均重新设计；18处地名采用本次新设计名称。普通标签改为横向象牙玉签，建筑、山丘和植被更圆润，延续 designs 已确认的手绘材质。

## 成图与来源

- [2560 × 1080 成图](world-map-original_2560x1080.png)：高质量重采样导出。
- [1931 × 814 原生生成图](world-map-original.png)：完整保留原始字节及内嵌来源元数据。
- [原图版本记录](world-map-original.png.generation.json) · [导出来源链](world-map-original_2560x1080.png.generation.json)。
- [实际提示词](source/world-map-original.prompt.txt) · [工具记录](source/tool-receipt.json) · [配置快照](source/config-snapshot.json)。
- [地名清单](map-names.json)；实际图像输入仅为 [designs 结伴同游样板](../team-ui-v2/team-ui-v2.png)。旧问道截图与上一版地图均未进入本轮图像输入。

## 本次原创命名

| 地域 | 名称 |
|---|---|
| 金 | 云砧岭、沉星矿谷、鸣金台 |
| 水 | 玄潮泽、月汐湾、听雨洲 |
| 木 | 竹风涧、青芽森、千藤庭 |
| 火 | 烛霞原、赤陶岭、丹炉谷 |
| 土 | 归元城、坤禾原、叠玉丘 |
| 生活聚落 | 桂灯集、听竹里、灵禾渡 |

标题为“五行奇谈／山海舆图”；当前位置为归元城；两个功能入口文案为“修行试炼”和“云外秘境”。

经查 image/docs、config、designs 与客户端地图说明，尚未发现已定稿的原创地图命名表；客户端仍使用旧参考体系。因此本表是本次新设计方案，不冒充历史已确认世界观。命名结合五行与项目原创宠物的竹风、玄潮、桂灯、赤陶等意象。此交付为静态视觉稿，未修改客户端地图ID或接入交互。

## 模型与验证

本次使用内置 image_gen，没有使用付费 API/CLI。2026-09-25 核对[官方发布公告](https://openai.com/index/introducing-chatgpt-images-2-5/)和[模型说明](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)，配置目标为 Images 2.5 / gpt-image-2.5-sunburst / max。

当前工具不开放 model、quality 参数；实际返回与C2PA只披露 ChatGPT / gpt-image 系列，具体为2.5还是2.0及质量档位均未确认。配置目标、实际提交和返回证据分开记录；没有把重采样尺寸当作原生生成尺寸。

主代理人工检查：18处地名及主标题、当前位置和两个入口完整；未见上一版问道地名；环水城、矿岭、竹林、湖泽、陶窑及田园构成独立的地貌关系。文件尺寸与SHA256记录核验通过。
