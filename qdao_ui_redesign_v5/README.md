# 五行奇谈 · UI 与场景重设计 v5

2026-09-11：当前通用控件、旧选服分层、HUD 和属性切片的交付与重建入口为 [v10 统一重切](../qdao_ui_style_recut_v10/README.md)。以下保留 v5 场景和整屏稿历史说明；历史整屏或 HTML 预览未全部换皮，不代表当前页面已实现。

日期：2026-09-06。游戏正式名称为 **五行奇谈**。本组重做登录、选服、选角、主城 HUD、森林石桥战斗背景和战斗入场过场，并提供 39 个通用 UI 控件。统一使用玉绿、米白、暖金，以及太极、葫芦、云纹装饰；人物沿用新版 Q 道童，登录与选角同行宠物统一为灵秀 Q 版九尾狐。

本组交付为**美术视觉稿、界面规范和演示文案数据**。游戏名已正式确认；服务器、角色、等级及槽位数量仍是演示内容，尚未确认生产业务。本次未接入 Unity、FairyGUI、登录服务、游戏服务器或战斗系统。

后续未完成项、实施顺序和新窗口接手任务见 [五行奇谈后续交接](../docs/WUXING_QITAN_HANDOFF.md)。本文件说明本轮已经制作的视觉资产。

## 视觉稿与场景

| 页面 | 标准导出 | 来源图与制作记录 |
|---|---|---|
| 01 登录 | [01_login_2560x1080.png](01_login_2560x1080.png) | [来源图](source/01_login.png) · [提示词](source/01_login.prompt.txt) |
| 02 选择服务器 | [02_server_select_2560x1080.png](02_server_select_2560x1080.png) | [来源图](source/02_server_select.png) · [提示词](source/02_server_select.prompt.txt) |
| 03 选择角色 | [03_character_select_2560x1080.png](03_character_select_2560x1080.png) | [来源图](source/03_character_select.png) · [提示词](source/03_character_select.prompt.txt) |
| 04 主城 HUD | [04_main_city_hud_2560x1080.png](04_main_city_hud_2560x1080.png) | [合成来源图](source/04_main_city_hud.png) · [当前重建流程](../qdao_ui_style_recut_v10/README.md#确定性重建) |
| 05 战斗场景 | [05_battle_scene_2560x1080.png](05_battle_scene_2560x1080.png) | [来源图](source/05_battle_scene.png) · [提示词](source/05_battle_scene.prompt.txt) |
| 06 战斗入场/加载过场 | [06_battle_entry_loading_2560x1080.png](06_battle_entry_loading_2560x1080.png) | [来源图](source/06_battle_entry_loading.png) · [提示词](source/06_battle_entry_loading.prompt.txt) |

标准导出目标为 2560 × 1080；来源图的原生尺寸以 [manifest.json](manifest.json) 的实际记录为准。导出由 [export_ui.py](export_ui.py) 完成，需要尺寸适配时使用等比 cover 和重采样。导出尺寸不代表原生生成分辨率；具体原图、裁切与导出情况以清单为准。

## 给接手的 Codex

1. 制作或接入这些界面和场景时，先读 [UI_SPEC.md](UI_SPEC.md)，确认页面层级、演示流程和状态规则。
2. 从 [copy.zh-CN.json](copy.zh-CN.json) 读取文案与演示数据。**JSON 是文字真值**；若生成图中的字形、数量或文案与 JSON 不一致，客户端按 JSON 绘制，图片仅供视觉参考。
3. 需要重新导出尺寸时，读取 [export_ui.py](export_ui.py)，使用保留的 `source` 图片和脚本实际参数执行本地导出；修改美术内容时另存新版本和提示词。
4. 通用控件见 [components/README.md](components/README.md) 与 [组件清单](components/manifest.json)。状态资源、九宫格、文字边距和本地重建以组件说明为准；主城 HUD 的本地构建与透明图层另见 [hud/README.md](hud/README.md)。
5. 实际接入前拆出装饰底图与原生控件，替换演示数据，并由具体客户端任务确定资源引用、事件绑定和业务接口。

动态标题、服名、状态、角色名、等级、搜索输入和按钮文案由客户端原生文本渲染。视觉稿中已有的文字属于画面示意，不作为文字资产或业务数据来源。

## 页面内容

- **登录**：使用正式游戏名“五行奇谈”，展示 Q 道童、灵秀 Q 版九尾狐、当前服和状态，以“选择服务器”“进入游戏”为主要入口，并放置切换账号、公告和设置。账号登录业务未确认，本稿不含账号密码表单。
- **选服**：四类入口、服务器搜索、2 列 × 4 行的演示卡片和当前选择摘要。维护区服禁止进入，并有明确文字说明。
- **选角**：左侧三个人物槽位（两个人物、一个创建空位），中央展示选中道童与九尾狐，右侧展示角色信息；底部返回选服或进入仙境。
- **主城 HUD**：以 v4 主城人物预览为固定背景，用原生 SVG 和通用控件重做“战斗”“观战”“角色”三个既有功能入口；场景和人物保持原样，按钮事件尚未接入。
- **战斗场景**：重绘旧森林石桥背景，交付静态战斗场景；不包含战斗系统、角色动作或碰撞与导航数据。

九尾狐采用灵秀的 Q 版仙侠气质：保留明确狐吻、尖耳和轻盈展开的九尾，避免团子猫感；登录与选角保持同一形象方向。

交互规范覆盖 normal、selected、disabled、维护禁入、空槽创建和搜索无结果。状态通过文本、图标或形状辅助表达，不只依赖颜色。完整细节见 [状态与流程规范](UI_SPEC.md)。

## 通用控件与主城透明 HUD

本轮共有六张标准视觉稿，以及 **39 个 SVG、39 个 PNG 通用控件**。控件源文件、三态与九宫格说明见 [通用控件文档](components/README.md)，目录索引见 [组件清单](components/manifest.json)。

主城 HUD 由代码组合现有场景、v10 新 AI 控件与独立文字，不单独调用生图生成整屏，也没有 `source/04_main_city_hud.prompt.txt`。它复用 v4 场景预览并叠加按钮；[source/04_main_city_hud.png](source/04_main_city_hud.png) 是合成效果图。可直接交接的分层资源如下：

| 资源 | 使用方式 |
|---|---|
| [无字透明皮肤 PNG](hud/hud_skin.png) · [SVG](hud/hud_skin.svg) | 客户端控件外观，文案另用原生文本层绘制 |
| [完整透明 HUD PNG](hud/hud_overlay.png) · [SVG](hud/hud_overlay.svg) | 已含三个按钮的中文标签，用于静态预览 |
| [独立标签 PNG](hud/hud_labels.png) · [SVG](hud/hud_labels.svg) | 查看文字排布；客户端动态标签以 JSON 为准 |
| [排布与制作记录](hud/placement.json) | 控件坐标、缩放、图层及实际检查记录 |
| [分层网页预览](hud/preview.html) · [HUD 说明](hud/README.md) | 查看背景与独立 HUD 图层，读取重建步骤 |

图片原生尺寸、导出尺寸和文件哈希见 [总清单](manifest.json)、[组件清单](components/manifest.json) 与 [HUD 排布记录](hud/placement.json)。本段记录视觉文件交付范围，不代表 Unity/FairyGUI 或按钮业务已经完成验收。

## 战斗入场、云气与遮罩

[06战斗入场](06_battle_entry_loading_2560x1080.png) 已沿用金发带Q道童和灵玥，画面通往新版森林石桥。它是独立过场插画，无加载条、百分比或提示文字；动态进度交给客户端。原生1931×814，等比适配为2560×1080。

[纯云气前景](06_battle_entry_clouds_fg_2560x1080.png) 是新版真RGBA，只保留米白玉绿暖金云气，中央透明，不含旧道童。原生1927×816 RGBA；导出保留Alpha，并清除1/255透明度量化残点。旧暗色遮罩原样复用：黑色RGB(0,0,0)、Alpha178，等效opacity=178/255。

[过场清单](transition_manifest.json) 记录三旧资源的新映射/复用理由、来源哈希与合成顺序；[构建入口](build_transition.py)由export_ui.py调用。根目录旧入场、云气和战斗背景路径已输出同尺寸兼容图。

六枚缺失徽标已补齐，总计十枚：太极、楼阁、莲花、山、炼丹炉、剑、水纹、罗盘、桃灵、火焰。圆徽标等比缩放，不作九宫格拉伸。原子控件与50旧切片另见[原尺寸重建](../exact_qdao_slices/README.md)，旧选服透明分层见[分层说明](../q_daoist_login_ui_uncropped_highres_final_layers/README_NATIVE_Q5.md)。

全库任务与后续接入边界见[交接](../docs/WUXING_QITAN_HANDOFF.md)。

## 相关素材与历史

- [主城与人物美术定调](../docs/QDAO_ART_DIRECTION.md)：原始参考、人物比例和风格约束。
- [游戏素材包 v4](../qdao_chibi_game_pack_v4/README.md)：标准主城背景、透明道童和排布预览。
- [历史宠物探索](../qdao_chibi_pets_v1/README.md)：保留早期三只宠物的独立素材；本组登录与选角已改用九尾狐。
- [AI 设计工具安装与交接](../docs/AI_DESIGN_TOOLS_SETUP.md)：其他电脑所需 Skills、MCP 和运行时安装说明。

v1/v3 已确认定调图和 v4 素材保留；旧登录兼容路径已按本轮授权更新为新版Q素材。本组未修改工具安装记录或 MCP 启用状态。
