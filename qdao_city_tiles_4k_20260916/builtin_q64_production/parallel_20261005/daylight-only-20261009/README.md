# 三张日景地图：当前总览与局部细节

2026-10-09。用户接受了“春节建筑、自然灰石地面”的方向，并要求预览更清楚。本轮已保存三张更新总览及三张独立AI细节近景，均完成图像解码、尺寸、SHA256及提示词/来源引用检查，见[验证记录](current-previews-validation.json)。

| 地图 | 看整体布局 | 看建筑与地面细节 | 近景原生尺寸 |
|---|---|---|---|
| 主城 | [当前总览v9](tianyong/tianyong-spring-natural-stone-v9.png) | [道馆、台阶与太极广场](tianyong/tianyong-natural-stone-detail-v1.png) | 1254×1254 |
| 渔村 | [当前总览v10](donghai-natural-stone-clear-routes-v10.png) | [中央三屋与双鱼广场](donghai-natural-stone-detail-v1.png) | 1254×1254 |
| 仙岛 | [当前总览v6](penglai/penglai-natural-stone-wall-trees-v6.png) | [花篮住宅与玉兔月饼庭院](penglai/penglai-natural-stone-detail-v1.png) | 1536×1024 |

三张总览实测均为1254×1254内置原生PNG，没有放大。近景由内置image_gen单独重绘，让建筑占据更多原生像素，展示屋瓦、朱红木作、窗花、石板细缝、燃后红纸和烟花筒；不是原图的精确坐标裁片，尚未通过拼接对齐，不能作为已完成的4K正式图块。

## 当前设计约束

只保留主城、渔村、仙岛三张物理地图的日景，春节、元宵、中秋自然混合，不划节日主题区。02/03小镇继续取消。其他13个旧制作线程保持停止归档，见[回执](stopped-threads.json)。

用户明确选择仙笺邮件的道家Q版、玉青/米白/柔金手绘质感。春节氛围落实到朱红墙裙与门窗、窗花、门联、灯笼和少量烟花实物。地板按最新更正恢复自然青灰/浅灰大石板、低对比细缝及单色石浅雕，取消红色及红金铺地；木廊、擂台、渔村沙土保留自身材质。地面稀疏鞭炮红纸是实体残留，不是红色地板。

树靠已有建筑、院墙或屋角。渔村路心与晒网区三处指定独立树坛已清除；仙岛明显独立海岸树和东北抬高药圃已移除。道路、台阶、侧巷和船坞入口在美术上连通，主城南北门外只用短路表示方向。

主城保留至少十处实际有顶功能建筑，含官府、道馆、通天塔、独立锁妖塔、地主宅、民宅，另有擂台。渔村保留中央三屋、双鱼广场、鱼市船坞及布店、武器店、首饰店。仙岛保留八仙各自八座住宅。

## 提示词、模型与来源

| 图片 | 实际提示词 | 逐图生成记录 |
|---|---|---|
| 主城总览 | [提示词](tianyong/tianyong-spring-natural-stone-v9.prompt.txt) | [来源](tianyong/tianyong-spring-natural-stone-v9.png.generation.json) |
| 渔村总览 | [提示词](donghai-natural-stone-clear-routes-v10.prompt.txt) | [来源](donghai-natural-stone-clear-routes-v10.png.generation.json) |
| 仙岛总览 | [提示词](penglai/penglai-natural-stone-wall-trees-v6.prompt.txt) | [来源](penglai/penglai-natural-stone-wall-trees-v6.png.generation.json) |
| 主城近景 | [提示词](tianyong/tianyong-natural-stone-detail-v1.prompt.txt) | [来源](tianyong/tianyong-natural-stone-detail-v1.png.generation.json) |
| 渔村近景 | [提示词](donghai-natural-stone-detail-v1.prompt.txt) | [来源](donghai-natural-stone-detail-v1.png.generation.json) |
| 仙岛近景 | [提示词](penglai/penglai-natural-stone-detail-v1.prompt.txt) | [来源](penglai/penglai-natural-stone-detail-v1.png.generation.json) |

本批仅使用宿主内置image_gen，没有调用单独计费API。配置目标为GPT Image 2.5 Sunburst/max；工具未提供型号/质量选择器，也未披露实际版本与质量，所有记录按证据保留null，不把提示词或配置当作实际返回值。

## 正式制作边界

本轮交付的是设计预览，尚无本方案通过验收的正式4K图块。正式单块仍要求4096×4096及真实细节来源，最终世界范围、网格与总数量尚未冻结。独立近景会解释或新增微小细节，正式分块仍需统一坐标、地物和接缝。

渔村与仙岛的世界面积目标各为主城3/4；同图5000人分散活动仍待角色占地、导航、可走面积及实际运行验证。[面积估算](capacity-5000-planning.md)不是测试报告。本轮没有修改客户端。旧版本不计入当前地图数量；最终游戏资源导出及当前引用核验后按项目规则清理被替代图片，逐图来源文字记录保留。
