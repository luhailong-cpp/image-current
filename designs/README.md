# 当前已确认风格与地图成图索引

此入口于 2026-10-10 根据仍在磁盘上的当前批准素材恢复，供主城、渔村、八仙岛继续制作时查阅。本文件不重建已删除旧图，不改变历史来源记录，也不代表正式游戏分块已完成。

## 当前风格参考

首要参考是用户亲自提供并已保存的 [道家 Q 版邮件风格图](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/user-references-20261009/mail-daoist-style.jpg)。其来源和用途记录在 [用户参考图清单](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/user-references-20261009/manifest.json)。本次已实际查看该图，并核验为 1932×814、SHA-256 `c1ab2e50b271e5c5590a92fe68bd6cf7d2c64cbd0d369b25b4ff5c6619033b63`。

旧路径 `designs/mail-ui-v1/01-mail-event.png` 当前缺失。后续新请求使用上述用户原始 JPG，加上对应地图的当前 detail 图承接画法、材质和视觉完成度；这是相同用户已确认方向的可用参考替代，不是更换风格。不得把 JPG 冒称为旧 PNG 的同一文件或相同哈希，不回写旧生成记录中的引用、模型、质量或来源。

取圆润饱满、明亮干净、细腻完成的道家 Q 版表现；以玉色、象牙白、柔和金色及春节建筑红色点缀协调。邮件界面本身、文字按钮、人物和夜景背景不画进地图。三张地图均为日景。

## 三张地图的当前参考

| 地图 | 整体布局参考 | 近景材质与画法参考 | 已核验尺寸 |
|---|---|---|---|
| 主城 | [自然石地 v9](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/tianyong/tianyong-spring-natural-stone-v9.png) | [主城 detail v1](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/tianyong/tianyong-natural-stone-detail-v1.png) | 概览 1254×1254；detail 1254×1254 |
| 渔村 | [自然石地、连通道路 v10](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/donghai-natural-stone-clear-routes-v10.png) | [渔村 detail v1](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/donghai-natural-stone-detail-v1.png) | 概览 1254×1254；detail 1254×1254 |
| 八仙岛 | [自然石地、贴墙树木 v6](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/penglai/penglai-natural-stone-wall-trees-v6.png) | [八仙岛 detail v1](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/penglai/penglai-natural-stone-detail-v1.png) | 概览 1254×1254；detail 1536×1024 |

概览负责建筑位置、道路和分区关系。detail 是独立近景重绘，用于材质和绘制完成度，不能当作严格坐标裁片。正式制作时实际附上对应概览、对应 detail、可用风格 JPG，以及必要的相邻原生图；参考输入数量遵循入口实际限制。既有有效原生相邻图优先用于连续几何与接缝。

## 用户最后确认的地图要求

- 主城、渔村、八仙岛三图；取消的 02、03 小镇与夜景不恢复。三种节庆自然混合，不另划春节、元宵、中秋专用区域。
- 建筑本体体现春节：墙裙、门框、红门、窗花、春联、屋檐灯笼共同形成气氛；元宵鱼灯／宫灯和中秋月饼、玉兔等作适量点缀。
- 地板使用自然浅灰、青灰石板，砖缝细且低对比；因地点保留木台、沙土等材质变化。地板不改回大面积红色或红金装饰带。
- 地面有少量烧过的鞭炮红纸、残留烟花筒、焦痕；建筑墙边可有烟花盒／筒。它们是小道具，不能堵主路。
- 树贴既有建筑、院墙或转角种植；桃花、银杏、白花树、绿色树、柳树适量混用。不要独立站在广场或主路的树岛，也不要盆栽充数；不凭空加墙来围树。
- 道路、院门、台阶、房前与船厂进出应视觉连通。主城南北只以门和短路表示连接，路很快接到画面边缘，不扩大门外空地。逻辑连接为岛→主城北侧、主城南侧→渔村北侧。
- 主城至少十个实际有屋顶的功能建筑，包括官府衙门、道馆、通天塔、单独的锁妖塔、地主宅和民宅；保留擂台。不能拿城门、角楼或开放亭子充当住宅数量。
- 渔村保留中央红屋及两侧蓝屋三座建筑、双鱼广场、布店、武器店、首饰店、鱼市及有未完工船只的船厂；船厂有进出通道。
- 八仙岛保留八位仙人各自独立居所，左右各四处；大殿、亭子和门另计，庭院、横路与环路连通。
- 渔村和岛的世界面积各为主城的 3/4；不是边长乘 3/4。5000 人分散活动仍需角色比例、连续通路和客户端运行验证，不能由美术图片像素数直接宣称通过。

正式 4096 图块继续按当前生产合同及真实原生像素要求制作；不能放大概览冒充清晰的游戏成品。新图继续使用用户授权的内置入口；逐图记录实际可得的模型、质量、时间、提示词和来源证据。入口未披露的实际型号／质量保留未确认状态。
