# W 斜背身份与施法交接

W 身份锚图为 `design/W.png`，真正后脑、披肩背、坐骨及近侧后足视角，保留原葫团团的单尾、金发带左侧结、玉绿披肩与胸前葫芦。原生 1254×1254 RGBA，完整画布缩放为 1024×1024；没有裁切、镜像、平移或 alpha 阈值清理。名义锚点 [512,942] 与实际坐姿支撑的近似偏差见 `design/W.png.generation.json`。

`runtime/cast/W/01.png` 至 `16.png` 已全部实际内置 AI 绘制，每帧 45 ms，共 720 ms。第 8–10 帧按邻帧单独 AI 重绘，已选 r2，替换原因和旧 SHA 保存在 `records/rejected-cast-W-*.generation.json`。旧拒稿 runtime 与本任务 source 图片已删除；逐图文字记录保留。

逐图记录在图旁，原生记录位于 `source/cast/W/*.png.generation.json`。配置目标 GPT Image 2.5 Sunburst/max，工具未开放型号/质量选择器且未返回可核验型号；实际 model/quality 均为 null。每张有独立 prompt、工具 output_hint receipt、实际调用返回时间、引用路径与 SHA。01 的旧自循环来源引用已修复。

独立预览为 `preview/cast-W/index.html`，支持 45 ms 正常播放、0.25 慢放、上一帧/下一帧和滑块；`preview/cast-W/contact.png` 是完整画布 4×4 联系表。16 张均逐张实看，浏览器实际正常/慢放与截图抽查完成；具体范围和限制见 `records/cast-W-review.json`。技术结果 `records/cast-W-technical.json`：16/16、1024 RGBA、透明范围 0–255、16 唯一 SHA。保留少量生成低 alpha 残留，未为隐藏边缘问题修改像素。

尚由主任务汇总六组 manifest、总 README/STATUS/MERGE_HANDOFF、所有原生在制图的最终保留清理，以及整宠物级别播放验收。这里不声称已接入客户端，不修改 Git 或旧资源。当前选定原生 source 图片留到主任务完成整包 QA 后按保留规则清理；先保留现有文字来源链。
