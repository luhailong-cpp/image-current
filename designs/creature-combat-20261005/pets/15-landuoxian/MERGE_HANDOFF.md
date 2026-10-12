# 岚铎仙素材接入交接

素材完成；本次未接入客户端。唯一制作目录是本文件所在的 `15-landuoxian`，没有改动公共包、其他对象或 Git 索引。

## 正式资源

以 [manifest.json](manifest.json) 的 `frames` 或六个 `groups` 为清单，加载 `runtime/<action>/<direction>/<两位帧号>.png`。全部 1024×1024 RGBA PNG，保留 Alpha；不得把棋盘预览或 contact 图片作为角色资源。

|action|方向|编号|时长|建议素材事件|
|---|---|---|---|---|
|hit|E / W|01–06|40 ms/帧，共 240 ms|03：hit_peak|
|attack|E / W|01–12|30 ms/帧，共 360 ms|07：attack_release|
|cast|E / W|01–16|45 ms/帧，共 720 ms|09：cast_release|

事件帧从 1 编号，表中事件是素材建议，尚未绑定任何客户端攻击判定或技能系统。单次动作按清单顺序播放后交回待机状态；预览的循环仅用于检查。历史逐图记录中的 `spell_release` 与最终清单的 `cast_release` 同指施法第 09 帧，接入命名以 manifest 为准。

E：斜前朝右下；W：真正斜后朝左上，独立绘制，禁止用镜像 E 替代。墨靛发玉衣仙童，解剖右手金框与三玉铎，左手玉槌，保持原有身份；没有移动循环。

## 尺寸和锚点

整张原生画布统一缩放到 920×920，粘贴到 1024 透明画布顶部坐标 `(52,37)`；没有逐帧裁紧、平移找脚点、镜像或插值补帧。PNG 已完成导出，接入时不要再次应用这一变换。

清单的 `pivot: [0.5,0.08]` 使用左下归一化坐标，约对应顶部像素坐标 `anchorTopLeft: [512,942]`（取整）。浏览器红十字是这一目标脚点，不是图片内容。所有帧使用同一锚点；自然屈膝、回弹、抬足以及绘制细节可能让实际足底变化，不要把目标点解释为每帧支撑足逐像素重合。

若后续引擎采用顶部归一化坐标，应换算 y≈0.92；若打图集裁边，必须保留原画布尺寸和每帧 trim offset 才能还原固定 pivot。本次不规定未读取的客户端 pixels-per-unit、压缩、碰撞或混合设置。

## 验证与来源

[SHA256SUMS.txt](SHA256SUMS.txt) 覆盖全部 68 张成品。[validation.json](validation.json) 是文件检查，[visual-review.json](visual-review.json) 是静态和浏览器检查；两者都不代表游戏运行验收。建议接入后检查实际显示大小、足点、透明边缘、前后方向、事件时间以及动作结束回待机。

逐图记录路径由 manifest 的 `generationRecord` 给出；不要假定所有记录都与 PNG 相邻。命中帧和普攻主要使用 `runtime/**/*.png.generation.json`，施法使用 `provenance/cast/**/*.generation.json`。原始模型目标、实际提交和返回值分开记录，实际型号/质量未确认。

本地原生与中间图清理情况见 [cleanup.json](cleanup.json)。被清理的来源引用带 `removedAfterProduction`，原提交参数和回执保留历史原文。外部原身份和已确认风格参考未删；宿主缓存不在本任务写入范围。

预览和清单可用 `python build_delivery.py` 重新生成（需要 Pillow），再用 `python audit_provenance.py` 检查来源。重建只读取当前成品，不会重新生成 AI 像素。已通过的视觉结论绑定每帧 SHA，若 PNG 修改，重新构建会将该帧恢复为待验收。
