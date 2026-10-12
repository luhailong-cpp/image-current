# 云啾啾 E 向施法 09–16 帧检查

2026-10-05。负责范围为E施法后半段09–16，共8帧，每帧45ms；01–08由主窗口负责。本段使用内置`image_gen`真实逐帧生成，没有复制、镜像、插值、整体平移补帧或逐帧重新对脚。

已逐张查看实际生成输出，并实际`view_image`查看 [cast-E-late-contact.png](../preview/cast-E-contact.png)。总览包含主窗口的01–08，用于看08→09衔接；本文件的逐帧检查结论范围为09–16。**这里只完成原生静态检查；正常速度/0.25倍速动态播放、统一1024导出与客户端接入仍由主窗口验收。**

## 当前选定源与记录

|帧|选定PNG|生成记录/实际prompt|
|---|---|---|
|09|source/cast-E-09.png|records/cast-E-09.json；prompts/cast-E-09.txt|
|10|source/cast-E-10-r1.png|records/cast-E-10-r1.json；prompts/cast-E-10-r1.txt|
|11|source/cast-E-11-r1.png|records/cast-E-11-r1.json；prompts/cast-E-11-r1.txt|
|12|source/cast-E-12-r1.png|records/cast-E-12-r1.json；prompts/cast-E-12-r1.txt|
|13|source/cast-E-13.png|records/cast-E-13.json；prompts/cast-E-13.txt|
|14|source/cast-E-14.png|records/cast-E-14.json；prompts/cast-E-14.txt|
|15|source/cast-E-15.png|records/cast-E-15.json；prompts/cast-E-15.txt|
|16|source/cast-E-16.png|records/cast-E-16.json；prompts/cast-E-16.txt|

导出按记录内的`action:cast,direction:E,frame`编号映射，不按候选文件名猜测版本。`records/cast-E-10.json`已标记superseded，不再选用。

## 逐帧所见

|帧|静态检查|
|---|---|
|09|高V蓄能峰值，白/青绿/灰褐羽层清楚；玉白光珠位于上胸/喙前，太极坠和双足未遮。09按分工使用既有03为过渡参考，不把03冒称相邻08。|
|10|r1为高V向水平释放之间的开翼过渡，翼尖仍高于肩，避免旧稿提前下垂/折叠；光效缩为小前送云光。|
|11|r1释放峰值，两翼向前下挥，小型云气完整留在画布内；稳定09作为编辑底稿，修复旧候选为巨型云气而整体挪动足云的问题。|
|12|r1回弹，双翼近水平并放松，颈部稍回正，云气变小变淡；两足仍在原云垫上。|
|13|双翼降到水平以下，光效仅剩淡云痕与稀疏微光，头颈回正。|
|14|双翼往躯干收回，羽尖略张；光效消失，坠饰仍为同一项链。|
|15|近收翼，轻微眼睑放松与肩羽回弹，未新增饰物或改变足序。|
|16|独立收势，喙闭合、眼神警觉，羽片和颈部细节区别于设计/首帧；不是复制图。|

本段保持E斜正面朝右下、同一白羽红冠幼鹤、金环、青绿金边领巾和单个太极坠。两翼两足一尾、一个祥云垫，无人形手臂/手指，未见缺肢或多肢。完整红冠、翼羽、尾和云垫均留在画布内。高举→前送→回弹→收翼的姿态推进可从总览辨认，最终动态节奏与连续性仍需主窗口实际播放判断。

## 来源与技术核对

[cast-E-09-16-technical.json](cast-E-09-16-technical.json)：8/8当前源记录SHA一致，全部原生1254×1254 RGBA，alpha范围0–255，无重复可见像素、无缺帧；alpha>16主体未触边。足部金色阈值包围框相对design-E的水平边界偏差约−8..+3原生像素，没有旧11候选约40px的整体左移。该颜色诊断不是自动对齐指令，也不代替动态站稳验收；源像素未因检查改变。

每次实际附上E方向设计、原`03_yun_jiu_jiu`身份与确认画法参考；另附的既有帧/编辑底稿均准确写入records。09/13–16沿用现有prompt；10/11失败后，经主窗口明确允许，另存实际修复prompt，12使用同样限制小型云气与稳定足云的专项prompt。实际prompt与输入顺序均保留，未用描述替代真正附图。

本段11次成功生成对应8张选定源和3张不选用候选：`cast-E-10-r0`因右侧特效裁切拒稿；`cast-E-10`因云气偏大/收翼过早被r1替代；`cast-E-11-r0`因巨型释放云气造成足云整体左移拒稿。均有独立prompt、真实返回路径与来源记录，记录已设`selected:false`。候选图片暂保留，待主窗口成品落盘并核验引用后统一按项目保留政策清理；文字记录保留。

配置目标沿用本批`gpt-image-2.5-sunburst/max`。工具未暴露型号/质量参数或可靠返回元数据，所有实际model/quality均为null；各记录保存当次配置快照、实际提交参数、真实outputHint、时间与原生SHA。未使用收费API/CLI路径。未改04–08、工具、根manifest或根交付文档。


最终收尾：本文件保留制作阶段的原生静态检查历史；原生动作/拒稿/过程图片已按cleanup.json清理，最终runtime及播放检查以../README.md、../manifest.json和final-review.json为准。上文“待主窗口检查”属于当时状态。
