# 西北分区制作状态

制作进行中。2026-10-10 已解除容量/布局门控，恢复内置工具原生绘制。原64块中，r03_c04、r03_c05、r04_c04、r04_c05已交给 accelerated-yamen-north；本目录当前负责60块。不等待游戏运行或5000人容量验证。

当前连续3×2区域 r05_c04、r05_c05、r05_c06、r06_c04、r06_c05、r06_c06 已完成内部及共同边检查，六张4096×4096已打包。首四块保留deeb69ed9f705a70版本及161处通过记录，新增两块各33处内部检查、三条共同边22处检查均通过；96张原生源与宿主输出逐一核对一致。外圈邻块尚未全部绘制，正式验收数仍为0；整个西北60块尚未完成。当前继续修复西侧r05_c03、南侧r07_c04，并绘制r05_c07等下一批。最新统计与逐片状态以 [progress.json](progress.json) 为准。

## 当前文件

- [最新六张4K原图ZIP](joint-six-tile-review/ac2031be4f9bb37b/northwest-six-4k-tiles.zip)
- [六块预览（1536，非正式原图）](joint-six-tile-review/ac2031be4f9bb37b/preview-only-1536.png)
- [六块交付与QA摘要](joint-six-tile-review/ac2031be4f9bb37b/delivery-summary.json)
- [四张4K原图ZIP](joint-2x2-r05_c04-r06_c05/deeb69ed9f705a70/northwest-2x2-4k-tiles.zip)
- [联合8192原图](joint-2x2-r05_c04-r06_c05/deeb69ed9f705a70/joint-8192.png)
- [浏览缩略图（1600，非正式原图）](joint-2x2-r05_c04-r06_c05/deeb69ed9f705a70/preview-only-1600.png)
- [交付与QA摘要](joint-2x2-r05_c04-r06_c05/deeb69ed9f705a70/delivery-summary.json)
- [像素来源与裁切证明](joint-2x2-r05_c04-r06_c05/deeb69ed9f705a70/joint-assembly.json)
- [最终64片原生来源审计](joint-qa/sources-audit-20261011-microrepair-selected.json)

本次QA覆盖四块内部、共同边及交点，外部未绘制的邻域仍需后续闭合。旧门控、旧候选和旧进度文件是历史状态，不表示仍暂停。

## 工具与证据

美术坐标画布65536×65536，每块4096×4096，采用4×4片原生1254图；核心1024、单侧上下文115、相邻重叠230。layout-only只是定位引导，不计正式画质。

- production_v2.py记录逐片坐标、实际参考、请求、回执、原生源和版本选择。
- assemble_native.py使用原生像素二值路径机械拼接，导出24段接缝及9个交点。
- assemble_2x2_v3.py已输出8192整图、同图精确切出的4张4096、像素来源索引与完整派生证据；--all-seams导出112段接缝及49个交点。全部67,108,864个输出像素已逐点验证来自所选原生源，四张4K与联合图精确裁切相同。局部切线配置与源哈希绑定，保留历史版本。
- refresh_progress.py应用已批准的4块归属排除并更新本目录60块统计，避免旧64块统计覆盖新归属。

只使用内置image_gen。正式原图和拼接不做放大、变形、调色、羽化或模糊遮缝。每个native/*.png.generation.json绑定提示词、实际提交参考图与哈希、请求、工具回执和宿主输出。内置工具未公开实际模型/质量，actualModel和actualQuality保持null，不把配置目标当执行证明。

当前参考为已确认白昼总览、自然石材细节和用户道系风格JPG；历史缺失mail PNG的记录保留，不改写为新引用。未修改客户端、公共配置、其他分区或Git。返修原图和凭据仍是制作依赖，不作破坏性清理。

