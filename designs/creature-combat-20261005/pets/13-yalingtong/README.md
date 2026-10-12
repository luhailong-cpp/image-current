# 芽铃童 · 战斗动作成品

**已完成：68张正式PNG，六组全帧、正常速度和0.25倍慢放检查完成。未接入客户端。**

沿用Image原有芽铃童：棕发橡果帽、苔绿短衣、双种铃悠悠球，每手一绳一铃；两臂两腿，右腰两种子袋，左腰红结短穗。没有制作移动循环。

## 规格

| 动作 | 每向帧数 | 帧时长 | 单次时长 |
|---|---:|---:|---:|
| hit 受击 | 6 | 40ms | 240ms |
| attack 普攻 | 12 | 30ms | 360ms |
| cast 施法 | 16 | 45ms | 720ms |

E为真斜前朝右下；W为独立绘制的真斜后朝左上。两向合计68张1024×1024 RGBA透明PNG。每组从01编号；pivot为左下归一化坐标[0.5,0.08]，顶部像素锚点[512,942]。普攻07建议impact，施法10建议cast_release。

## 预览与使用

[六组交互预览](preview/index.html)支持正常1×、0.25×慢放、暂停、单步、逐帧滑杆、透明棋盘/深底/白底。可直接打开本地HTML，不依赖联网。

preview目录同时提供六张全帧总览及12个512×512无损透明WebP（每组normal/slow各一）；这些是预览，正式资源为runtime中的1024 PNG。

- 正式资源：runtime/<hit|attack|cast>/<E|W>/01.png起。
- [manifest.json](manifest.json)：动作、方向、帧时长、锚点、事件、SHA与逐图记录索引。
- [SHA256SUMS.txt](SHA256SUMS.txt)：68张正式PNG校验值。
- [QA.md](QA.md)、[technical-audit.json](technical-audit.json)、[preview-audit.json](preview-audit.json)、[visual-qa.json](visual-qa.json)：最终验收与边界。
- [MERGE_HANDOFF.md](MERGE_HANDOFF.md)：接入交接。
- prompts、evidence及PNG旁的generation.json：逐图实际请求、工具返回证据、来源、SHA和修正历史。
- [POSES.md](POSES.md)、[MODEL_CHECK.md](MODEL_CHECK.md)：姿态约束和模型核对。

## 导出与来源

所有姿态均经宿主内置image_gen独立生成/编辑；未使用付费API/CLI。原生输出1254×1254；每方向在三类动作间使用同一变换：整张原生画布缩至922×922，置入1024画布的[51,55]位置。E/W恰好采用相同参数；没有逐帧对脚、裁切、镜像或插值造帧。生成有少量手绘纹理、支撑宽度和比例差异，固定锚点不表示每帧脚底像素绝对相同。

配置目标为gpt-image-2.5-sunburst/max；内置工具无model/quality选择器，也未返回实际型号和质量证据。每图实际提交的型号/质量选择值及actualModel/actualQuality均为null，不把配置目标写成已确认的实际值。

本包只保留正式图片和所需预览、设计、接入及文字来源文件，没有拒稿图片备份。旧输入路径被修正或统一导出覆盖时保留原提交SHA，并标记historicalPixels；无法用当前同名PNG代替当时输入。共享身份/风格参考只读保留。宿主生成缓存位于本任务唯一写入范围之外，未由本任务删除。

QA-hit/attack/cast-E/cast-W及各子任务technical-check是统一导出前的制作快照；其中旧SHA、包围盒或坐标不代表最终导出。最终资源以总manifest及technical-audit为准。

