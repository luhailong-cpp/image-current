# 五行奇谈：全库美术交付与接手说明

2026-09-23 素材保留要求更新：以 [项目规则](../AGENTS.md)为准，只保留最终游戏素材与配套设计；原图、回退版和中间图在成品与引用核实后删除。下文保留原图及历史副本的要求不再生效，历史 SHA 和生成文字记录仍可查阅。

2026-09-21 长期偏好：用户明确认可 [designs 现有成图](../designs/README.md)，后续必须按这种风格制作。继续作图先查看该成图索引，再按[统一图像设置](../config/image-generation.json)与[执行策略](IMAGE_MODEL_POLICY.md)核对最新正式 GPT Image 和最高质量。

2026-09-12 最新图片入口：[全库节庆精修已完成](../qdao_festival_refinement_20260910/README.md)，逐文件待处理为 0。人物 v9／v11、场景、登录前整屏及有效导出以本轮最终验收为准；下文各日期为历史交付与客户端专项范围。新素材继续保持道家 Q 版及少量春节／元宵／中秋点缀。

2026-09-11 属性网页续作：已补齐 [v10 可交互预览](../designs/attribute-panels/v10-preview/README.md)，复用22张正式切片，人物以属性窗口为主体、宝宝用四宠头像列表，保留无相性点与原加点模型。桌面／手机版及键盘交互验收通过；旧网页和v2静态图保留作历史。新增人物动作、高清主城与扩展场景仍由各自任务推进，全库节庆精修按既定前置完成顺序接续，不将本网页完成等同于全项目完成。

2026-09-11 当前 UI 入口：[v10 统一风格重切](../qdao_ui_style_recut_v10/README.md)，含六组内置原画、158 个正式 PNG 合同、逐件映射、全量验证与正式发布记录。复现执行 v10 的暂存、核验、发布流程；旧构建入口已阻止写回历史皮肤。3 个纯文字层保留，其余 155 个换皮／重裁；158 个正式 PNG 及关联文件已完成首次发布，支持文件和标准 02 选服／04 HUD 预览的最终同步以 v10 发布记录为准。并行客户端任务已同步 31 张属性 Sprite，并通过 [v10 Unity 验收](../designs/attribute-panels/v2-painted/unity-slices/unity-validation-v10.json)：两种分辨率共 10 张编辑器截图、26 项测试通过、0 项失败。此为离线样例数据验收，没有在线服务器验证，也不代表其余全库 UI 已接入。旧 Unity 报告、属性 HTML 与其他历史整屏稿不代表 v10 当前版本。用户已明确授权此次 UI 文档、素材提交并 push；下文 v6 的“仅本地”是历史任务边界。

记录日期：2026-09-06。素材仓库：`E:/work/image`。本轮起点是 `60134a6`；最终本地提交号用 `git log -1 --oneline` 查询。用户已将范围扩展为遍历目录，完成未更新的道家 Q 版素材、所有物件图标与切片，保持原尺寸，删除过程图并本地提交。

## 先看这几份记录

2026-09-11 人物差异化交付：01–22号职业人物以原创道家Q版重设计，全部直发/束发/辫发；保留24个旧路径与4096×4096 RGBA规格。当前[人物总览与交付](../qdao_character_diversity_v9/README.md)、[验收](../qdao_character_diversity_v9/validation.json)和[兼容映射](../qdao_character_diversity_v9/compatibility_map.json)取代旧v6人物状态。已发布的v8曝光修正沿用并核对来源链。本轮不代表v11新增23–28人物或客户端任务全部完成。

2026-09-10 UI 长期制作入口：[UI 制作规范第 2 节](../qdao_ui_redesign_v5/UI_SPEC.md#2-统一视觉与控件层级)。所有 UI 制作、实现与重新切图先读指定风格图和通用提示词，保留道家 Q 版与节庆方向；以后其他游戏截图默认只参考功能。

2026-09-09 后续任务：用户已授权在当前其他出图任务全部完成后，继续统一精修全库图片，整体保持道家 Q 版，加入少量春节、元宵、中秋氛围。接手先读[节庆氛围全库精修](QDAO_FESTIVAL_REFINEMENT.md)，其中记录监测对象、5 小时后开始且随后每小时检查的顺序，以及以最新交付为输入的执行要求。下文 v6 为历史交付记录，不能代替当前任务的完成核对。

1. [全库交付索引](../qdao_asset_refresh_v6/README.md)：人物、动作、物件、UI、场景、宠物的最终入口。
2. [全库验收结果](../qdao_asset_refresh_v6/validation.json)：对 `60134a6` 的 369 个视觉文件逐项比对；`status` 必须为 `passed`。
3. [清理记录](../qdao_asset_refresh_v6/cleanup.json)：已删除的旧过程图与本轮暂存目录。
4. [制作前逐文件审计](ART_ASSET_AUDIT.json)：原路径、像素尺寸、Git blob、SHA-256、家族与替换方案。此审计是历史基线，不是当前待办。

## 本轮交付

| 范围 | 最终结果与入口 |
|---|---|
| 战斗入场／加载过场 | [06 入场图](../qdao_ui_redesign_v5/06_battle_entry_loading_2560x1080.png)，新版金发带 Q 道童与九尾狐灵玥进入森林石桥；2560×1080，无烘焙进度文字 |
| 纯云气与暗色遮罩 | [真透明云层](../qdao_ui_redesign_v5/06_battle_entry_clouds_fg_2560x1080.png)，旧云气人物已移除；[映射](../qdao_ui_redesign_v5/transition_manifest.json)明确加载图、云气、战斗背景与遮罩。黑色遮罩沿用原 alpha=178，运行时可用 178/255 透明度实现 |
| 六枚缺失徽标 | 炼丹炉、剑、水纹、罗盘、桃灵、火焰全部补齐；[十徽标总览](../qdao_ui_redesign_v5/components/badges_overview.png)，通用组件合计39套 SVG＋透明 PNG |
| 旧切片、九宫格与原子控件 | [50 张切片](../exact_qdao_slices/README.md)全部按原尺寸重建；高分辨原子控件、十个420徽标、桃灵别名与旧母图兼容输出齐全，边距和缩放规则记录在清单 |
| 旧选服画面与分层 | [12 张旧路径输出](../q_daoist_login_ui_uncropped_highres_final_layers/README_NATIVE_Q5.md)完成新版替换；5120／10240档独立背景装饰层、按钮层、无字合成层与独立文字 SVG |
| 物件和法器 | [124 枚图标](../qdao_asset_refresh_v6/icons/README.md)全部重绘，原600×600 RGBA；FairyGUI 图集仍7912×6088，124帧名称、坐标和大小保留 |
| 静态人物 | [人物包](../q_daoist_character_pack_4096/README.md)22个职业人物逐张重绘＋2个统一道童参考，均4096×4096 RGBA；根目录7个旧道童路径改为已确认形象的兼容输出 |
| 人物动作 | [八方向行走](../character_move_8dir/README.md)全部32帧重绘，1254×1254 RGBA；脚底 y=1179，帧序与建议时长记录齐全 |
| 宠物透明素材 | [灵玥](../qdao_ui_redesign_v5/pet/README.md)与[葫团团、符小虎、云啾啾](../qdao_chibi_pets_v1/README.md)保留已确认设定图，另交付透明静态角色 |
| 场景与已确认作品 | 新版主城、原五张v5标准画面、已确认透明道童与宠物概念保留；旧主城／战斗路径映射到新图。六张标准画面均2560×1080 |

## 风格与尺寸约束

正式名只用“五行奇谈”。道童保持纯金发带、短棕发、圆眼笑脸、米白短袍裤、玉绿金边背心、太极葫芦与大头短身比例。职业人物以v9为当前定调：保留道家Q版、职业主题与法器，脸型、年龄、体态和服装独立设计，不再套用主角面孔；全部不用卷发。灵玥保持狐吻、尖耳、金眼、朱砂额纹、金玉项圈、白色淡紫蓝尾与九个可辨尾尖。

玉绿、米白、暖金、桃木为主要配色。九宫格只用于清单允许伸缩的框板和控件，圆徽标／人物／文字整体等比缩放。

“原大小不变”指原路径的像素画布；实际 AI 原生尺寸与放大导出分别记录。人物通常由1254方图透明处理后导出4096，图标来自4×4或4×3原生母表的独立格，动作由各方向2×2表提取；这些输出不冒称原生4K或每格600原生细节。上述为 v6 来源说明。当前 UI v10 使用内置生成原画、透明裁片与内嵌 PNG 的 SVG 包装，真实原生尺寸见 v10 生成记录。

## 清理与复现

旧五张物件源母图、旧图集 JPG 预览和两张诊断截图不再作为交付；本轮母表副本、切格副本、临时 GIF、`.work` 与生成缓存目录在验收后清理。正式图集、独立素材、完整提示词、处理脚本、JSON记录、被构建使用的来源和已确认参考图保留。无关的 `movement_diagnostics/move_20260905_082427.log` 原样保留。

普通位图先读取 [统一图像设置](../config/image-generation.json)与[执行策略](IMAGE_MODEL_POLICY.md)，使用内置 `image_gen`，按 `imagegen`、`generate2dsprite`／`generate2dmap` 处理；UI 图像按 v10 的指定风格原画与重切流程更新，原生文字和布局仍由客户端负责。环境安装说明见 [AI_DESIGN_TOOLS_SETUP.md](AI_DESIGN_TOOLS_SETUP.md)。参考图传递或工具的 Windows ACL 问题是本次环境记录，不能把旧会话路径当成另一台机器的现成能力。

```powershell
python qdao_ui_redesign_v5/export_ui.py --check
python qdao_asset_refresh_v6/icons/build_atlas.py --check
python q_daoist_character_pack_4096/build_manifest.py
python qdao_asset_refresh_v6/verify_assets.py
python qdao_ui_style_recut_v10/tools/validate_staged.py
git diff --check
```

人物／动作再生成需要内置生图和视觉验收；来源标识和提示词可复用，AI不保证像素级重现。图集和原生控件可由已交付单件与构建脚本确定性重建。

## 下一阶段：实际客户端

本轮是美术交付，未接入游戏。v5登录、选服、选角整屏仍是已确认视觉参考；已交付原生控件、独立角色／宠物以及旧选服分层，不能把这些等同于完整客户端页面。区服、等级、角色槽位仍为演示数据，文字真值在 [copy.zh-CN.json](../qdao_ui_redesign_v5/copy.zh-CN.json)。

实际接入时需先定位客户端工程，再完成页面排布与动态文字、选服状态／搜索／维护禁入、角色选择、按钮事件、动作播放、宠物挂载和场景切换。碰撞、导航、其他战斗动作或宠物动画需按真实运行需求制作；当前没有这些可替换的既有资源。不要把静态人物冒称动画或把素材截图当作引擎验收。

`wire_qdao_v3_assets.py` 对目录关系有历史假设，未确认真实工程路径前不执行。v6 当时仅授权本地提交；当前 v10 UI 任务已获用户明确授权提交并推送，实际结果以提交记录和远端核对为准。

## 后续窗口可直接粘贴

UI 制作／实现／重切还需先读 `qdao_ui_redesign_v5/UI_SPEC.md` 第 2 节；节庆方案和后续全库精修顺序读 `docs/QDAO_FESTIVAL_REFINEMENT.md`。下文 v6 交付为历史记录，当前状态以最新任务和验收为准。

> 在 E:/work/image 继续五行奇谈项目。先读 docs/WUXING_QITAN_HANDOFF.md、qdao_asset_refresh_v6/README.md 和 validation.json，核对本地 Git 状态。全库旧美术已按原路径、原尺寸统一为新版道家 Q 风格，勿重复重做已验收素材。若开始客户端接入，先定位真正客户端工程；使用现有独立人物、宠物、32帧动作、124图标、39控件、切片与分层清单，按真实数据和页面流程实现并在引擎中验收。保留无关日志。当前 UI 必须继续读 qdao_ui_style_recut_v10/README.md；此次 UI 提交和推送已获用户授权。
