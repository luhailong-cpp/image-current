# 五行奇谈 · 十枚圆徽标设计说明

日期：2026-09-06。制作入口为 [build.mjs](build.mjs)，本批沿既有 SVG 系统制作，未调用生图模型，也没有虚构生图提示词或记录。

## 完整制作指令

在已完成的四枚圆徽标上扩展六枚：炼丹炉、剑、水纹、罗盘、桃灵、火焰。每枚 120 × 120，使用同一 `badge()` 底盘，保留圆心、双层金框、玉绿渐变、桃木厚度与透明外缘阴影。原四枚及另外 29 枚组件不重新设计。

主图形用米白 `#FFF7DE`，结构与轮廓点缀用暖金 `#E8D197`，内部必要留空用玉绿 `#176C5F`；桃果明暗线沿用已有山形的浅玉绿 `#679682`。图形保持居中、完整、留有边框呼吸空间，清楚的外轮廓比细纹优先。素材内没有动态文字、人物、图片外链或脚本。SVG 与透明 PNG 均独立交付；只能等比缩放，不能九宫格拉伸。

实看旧母图后确认：炉为带盖双耳支足丹炉；剑为竖直向下剑刃和横向护手；水为旋涡水浪；罗盘为多向外盘与中心指向；桃灵是桃果、叶片和花卉意象，不是有脸小人；火为上扬火舌和内卷火芯。重绘保留这些符号语义，以宽主形和有限内部留空确保 120/48/32 px 预览中可区分。新的桃灵保留桃果、桃叶与中缝，省略旧母图的花朵细饰。

## 旧资源与新版的对应

旧目录为 [q_daoist_login_buttons_redrawn_atomic](../../q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/)，母图为 [ai_qstyle_badges_sheet_chroma.png](../../q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/ai_qstyle_badges_sheet_chroma.png)。旧文件名继续保留。用户扩大范围后，旧原子目录已补齐对应的 420 × 420 新版透明徽标和母图；本目录 `svg/` 和 `png/` 保留 120 × 120 设计源。

| 旧文件 | 新 ID | 本批状态 |
|---|---|---|
| `icon_yin_yang.png` | `round_badge_taiji` | 沿用已完成 |
| `icon_pagoda.png` | `round_badge_pagoda` | 沿用已完成 |
| `icon_lotus.png` | `round_badge_lotus` | 沿用已完成 |
| `icon_mountain.png` | `round_badge_mountain` | 沿用已完成 |
| `icon_cauldron.png` | `round_badge_furnace` | 新补齐 |
| `icon_sword.png` | `round_badge_sword` | 新补齐 |
| `icon_water.png` | `round_badge_water` | 新补齐 |
| `icon_compass.png` | `round_badge_compass` | 新补齐 |
| `icon_peach_spirit.png` | `round_badge_peach_spirit` | 新补齐 |
| `icon_fire.png` | `round_badge_flame` | 新补齐 |

该表说明符号替换关系。这套 v5 组件的原始设计尺寸为 120 × 120；旧原子目录中 10 枚独立徽标已从矢量源按 420 × 420 导出，另外提供 `icon_leaf.png` → `icon_peach_spirit.png` 兼容别名。旧母图按原 1774 × 887 像素和原单元位置重建为真 RGBA。完整记录见 [旧路径重建清单](../../exact_qdao_slices/manifest_native_q5.json)。功能名称和客户端路由仍由真实业务确定。

## 验证与预览

[十枚总览](badges_overview.png) 展示全部原尺寸徽标与 48/32 px 小尺寸；[验证记录](badge_validation.json) 记录文件检查。预览上的中文和 ID 仅用于对照，不进入素材。徽标原生文字标签、交互和客户端接入不属于本次完成项。
