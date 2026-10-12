# 五行奇谈 · 14只原创宠物素材包

2026-09-24 用户要求重新设计身份与关键造型元素，神兽、变异、元灵也采用原创方案。本目录为新的正式工作目录；旧 `pets-20260924` 是未采用候选，仅保留来源证据。

14 只原创宠物的 28 张独立原生母图及 56 张正式透明导出已齐全。新图只采用 `designs/` 已确认画法作风格参考；W 额外引用同宠的新 E 图保持身份，分别绘制真实斜后视。旧候选未参与本包生成或正式导出。

## 原创名单与用途槽位

旧名称只标识用户最初要求替换的用途槽位，不是新图身份，不代表现有客户端模型 ID；真实 `clientModelId` 尚未提供。

| 编号 | 新名称 | 资源 ID | 原用途槽位 | 新造型 |
|---|---|---|---|---|
| 01 | 烛翎 | `01-zhuling` | 火鸦 | 靛蓝短尾鸦，铜红翼斑 |
| 02 | 绛铃 | `02-jiangling` | 粉衣仙子 | 墨黑短发纸偶女，绛红短斗篷，折扇铃 |
| 03 | 霜团貂 | `03-shuangtuan` | 雪狐 | 珠灰短胖貂，深靛短耳，浅玉宽扁尾，织围巾 |
| 04 | 桂灯童 | `04-guideng` | 秋棠仙子 | 栗发男童，叶帽，木柄桂花灯 |
| 05 | 砚羽灵 | `05-yanyuling` | 羽鹤仙卿 | 暮紫胖猫头鹰，砚包，卷轴 |
| 06 | 汐螺 | `06-xiluo` | 精卫 | 青瓷壳蟹灵 |
| 07 | 苍嶂麟 | `07-cangzhanglin` | 应龙 | 无翼玉甲四足麒麟 |
| 08 | 竹风狸 | `08-zhufengli` | 青鸾 | 棕狸，单竹叶滑翔披肩，环尾 |
| 09 | 赤砂魁 | `09-chishakui` | 景云 | 赤陶小守卫，靛衣，窑炉包，短石锤 |
| 10 | 玄潮龟 | `10-xuanchaogui` | 墨渊 | 黑青灵龟，浅玉水盂背甲 |
| 11 | 霞角鹿 | `11-xiajiaolu` | 赤天 | 可可棕斑点鹿，淡紫杏晶角，无翼 |
| 12 | 月弦师 | `12-yuexianshi` | 玉霄 | 栗发长侧辫少女，靛蓝象牙衣，站立持月牙弦琴 |
| 13 | 芽铃童 | `13-yalingtong` | 九华 | 橡果头盔，苔绿短衣，双种铃悠悠球 |
| 14 | 绯耳灵 | `14-feierling` | 白琉影 | 铜红发狐男，深玉短衣，单黑尖尾，木狐面具 |

逐宠实际造型差异见 [原创差异审查](records/originality-review.json) 及各自 `records/<slug>-visual-review.json`。已核对新身份、轮廓、服装、装饰、主要道具与 E/W 朝向；这是素材视觉审查，不代表用户逐只确认或法律结论。

## 技术规格与交付

- 本批 28 张原生来源均为 **1254×1254**；保留原生 PNG 与逐图来源记录。导出只缩小，不制造放大 4K。
- `source/<slug>-E.png` 和 `-W.png`：分别生成的方向图。E 为敌方左上朝向右下；W 为我方右下朝向左上，不以镜像冒充背面。
- `runtime/<slug>/idle_E.png`、`idle_W.png`：1024×1024 真透明 RGBA，同宠两向共用缩小因子与脚点 `(0.5,0.08)`，以左下为原点；不放大。
- `ui/<slug>/fullbody_1024.png`：E 全身同源图；`portrait_512.png`：实际新母图人工取景头像，不复用旧裁切坐标，不把全身缩图当头像。
- `prompts/`、`records/`：新图真实提示词、调用证据、元数据检查和批次设置；原图旁 `*.generation.json`、派生图旁 `*.derived.json` 链接 SHA256 和处理记录。
- `previews/`：正向、双向与头像总览均由正式 PNG 排版，未额外补画角色。

本包为**静态双朝向**，不包含动画、客户端替换、数据表修改或 Unity 引擎验收。技术验证、原创差异审查、用户确认和引擎验收分别记录，不互相代替。

## 增量构建

```powershell
python designs/pets-original-20260924/build_pack.py --only 01-zhuling
python designs/pets-original-20260924/build_pack.py
python designs/pets-original-20260924/build_overviews.py
python designs/pets-original-20260924/build_portrait_overview.py
python designs/pets-original-20260924/validate_pack.py --require-complete
```

[asset-config.json](asset-config.json) 保存名单和实际源图的头像、脚点参数。缺少同宠任一方向时只诊断和归档证据，待两向都到后计算共同尺度。输入和设置不变时不重写字节未变的文件。

处理保留原生透明，只清除已授权的极小孤立噪点与远离主体的 alpha=1/255 底噪，原始 PNG 不变。若工具返回不透明洋红背景，优先清除边界连通背景；玄潮龟E另对人工确认的绳结封闭缝隙按源图哈希与小矩形范围清理透明度。范围、像素数和操作均写入派生记录，保留原生源图及角色本色。

模型配置目标、工具提交参数、实际返回值与 C2PA 软件信息分别记录。工具不披露型号或质量时相应实际字段保留 `null`，不以提示词、配置或公告冒充已确认版本。


## 查看与使用

- [14只正向总览](previews/E-roster.png)
- [14只 E/W 双向总览](previews/EW-roster.png)
- [14只头像取景总览](previews/portrait-roster.png)
- [完整素材清单](manifest.json) · [技术验收](records/technical-validation.json) · [原始工具文件与来源审计](records/provenance-audit-20260924.json) · [最终视觉复查](records/final-visual-review.json)

每只 `runtime/<资源ID>/` 包含 `idle_E.png`（敌方斜前朝右下）和 `idle_W.png`（我方真正斜后朝左上），均为 1024×1024 RGBA。每只 `ui/<资源ID>/` 包含 `fullbody_1024.png` 和人工取景的 `portrait_512.png`。原生来源在 `source/`，每张旁有 `.generation.json`；每张正式导出旁有 `.derived.json`。

## 本批模型与来源记录

本批使用内置 `image_gen.imagegen`，当次配置目标为 GPT Image 2.5 / `max`。工具没有开放型号和质量选择器，28张PNG的 C2PA 只披露 `ChatGPT / gpt-image`，**不能确认实际为2.5还是2.0，也不能确认实际质量档位**；逐图 `actualModel`、`actualQuality` 均保留 `null`。配置目标、实际提交参数和实际返回证据分别保存，未使用付费 API/CLI。

28张源图与 receipt、保留的工具原文件逐张 SHA256 相同，与未采用旧候选没有相同文件复用。完整实际提示词在 [prompts](prompts/)，工具返回与参考输入通道记录在 [records](records/)。

| 宠物 | E生成记录 | W生成记录 | 战斗图目录 | UI图目录 |
|---|---|---|---|---|
| 烛翎 | [E](source/01-zhuling-E.png.generation.json) | [W](source/01-zhuling-W.png.generation.json) | [01-zhuling](runtime/01-zhuling/) | [01-zhuling](ui/01-zhuling/) |
| 绛铃 | [E](source/02-jiangling-E.png.generation.json) | [W](source/02-jiangling-W.png.generation.json) | [02-jiangling](runtime/02-jiangling/) | [02-jiangling](ui/02-jiangling/) |
| 霜团貂 | [E](source/03-shuangtuan-E.png.generation.json) | [W](source/03-shuangtuan-W.png.generation.json) | [03-shuangtuan](runtime/03-shuangtuan/) | [03-shuangtuan](ui/03-shuangtuan/) |
| 桂灯童 | [E](source/04-guideng-E.png.generation.json) | [W](source/04-guideng-W.png.generation.json) | [04-guideng](runtime/04-guideng/) | [04-guideng](ui/04-guideng/) |
| 砚羽灵 | [E](source/05-yanyuling-E.png.generation.json) | [W](source/05-yanyuling-W.png.generation.json) | [05-yanyuling](runtime/05-yanyuling/) | [05-yanyuling](ui/05-yanyuling/) |
| 汐螺 | [E](source/06-xiluo-E.png.generation.json) | [W](source/06-xiluo-W.png.generation.json) | [06-xiluo](runtime/06-xiluo/) | [06-xiluo](ui/06-xiluo/) |
| 苍嶂麟 | [E](source/07-cangzhanglin-E.png.generation.json) | [W](source/07-cangzhanglin-W.png.generation.json) | [07-cangzhanglin](runtime/07-cangzhanglin/) | [07-cangzhanglin](ui/07-cangzhanglin/) |
| 竹风狸 | [E](source/08-zhufengli-E.png.generation.json) | [W](source/08-zhufengli-W.png.generation.json) | [08-zhufengli](runtime/08-zhufengli/) | [08-zhufengli](ui/08-zhufengli/) |
| 赤砂魁 | [E](source/09-chishakui-E.png.generation.json) | [W](source/09-chishakui-W.png.generation.json) | [09-chishakui](runtime/09-chishakui/) | [09-chishakui](ui/09-chishakui/) |
| 玄潮龟 | [E](source/10-xuanchaogui-E.png.generation.json) | [W](source/10-xuanchaogui-W.png.generation.json) | [10-xuanchaogui](runtime/10-xuanchaogui/) | [10-xuanchaogui](ui/10-xuanchaogui/) |
| 霞角鹿 | [E](source/11-xiajiaolu-E.png.generation.json) | [W](source/11-xiajiaolu-W.png.generation.json) | [11-xiajiaolu](runtime/11-xiajiaolu/) | [11-xiajiaolu](ui/11-xiajiaolu/) |
| 月弦师 | [E](source/12-yuexianshi-E.png.generation.json) | [W](source/12-yuexianshi-W.png.generation.json) | [12-yuexianshi](runtime/12-yuexianshi/) | [12-yuexianshi](ui/12-yuexianshi/) |
| 芽铃童 | [E](source/13-yalingtong-E.png.generation.json) | [W](source/13-yalingtong-W.png.generation.json) | [13-yalingtong](runtime/13-yalingtong/) | [13-yalingtong](ui/13-yalingtong/) |
| 绯耳灵 | [E](source/14-feierling-E.png.generation.json) | [W](source/14-feierling-W.png.generation.json) | [14-feierling](runtime/14-feierling/) | [14-feierling](ui/14-feierling/) |

旧“0/28、0/56”描述的是 10:32 UTC 的准备阶段快照，已归档到 [接续历史](records/handoff-initial-0-of-28.md)；真实母图生成时间为其后。当前完成度以本 README、manifest 和最新验收报告为准。
