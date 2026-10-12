# 五行奇谈 · 主城三按钮 HUD

历史诊断截图已按本轮清理要求删除，三个入口的布局数据仍保存在本包。

本交付仅重做基线 `60134a6` 主城诊断截图右侧的 **战斗 / 观战 / 角色** 三个入口。使用 [v4 主城人物预览](../../qdao_chibi_game_pack_v4/preview-main-city_2560x1080.png)作为本次组合的背景来源，复用 [通用组件 primary_button_normal](../components/svg/primary_button_normal.svg)；当前按钮已更新为 v10 指定风格皮肤；背景与人物使用已有来源，三个入口的位置和独立文字层保留。组合步骤本身不再修改背景来源像素。

查看 [分层网页预览](preview.html) 或 [完整画面 PNG](../source/04_main_city_hud.png)。画布均为 **2560 × 1080**。

## 图层与位置

| 文件 | 用途 |
|---|---|
| `hud_overlay.svg` / `hud_overlay.png` | 完整透明 HUD，包含三个控件与可读中文标签 |
| `hud_skin.svg` / `hud_skin.png` | 无文字透明控件层，便于客户端原生叠字 |
| `hud_labels.svg` / `hud_labels.png` | 独立中文标签层；SVG 以 `<text>` 保留文字 |
| `placement.json` | 坐标、尺寸、字体、组件/背景 SHA-256 与验证结果 |
| `../source/04_main_city_hud.png` | 原背景与 HUD 的合成预览；不是替换背景资产 |
| [v10 构建流程](../../qdao_ui_style_recut_v10/README.md#确定性重建) | 当前暂存、核验与发布入口；旧 `build.mjs` 已阻止直写 |

三个按钮左上坐标依次是 `(2160, 176)`、`(2160, 280)`、`(2160, 384)`；每个 **336 × 81.6** 逻辑像素，右边距 **64 px**，上下间距 **22.4 px**。使用原组件 `460 × 112` 的统一等比缩放，不拉伸边框、阴影或云纹。透明画布之外没有额外底色。

中文为独立文字层，字号 **36 px**、字重 600、米白 `#FFF7DE`，优先使用 Microsoft YaHei，回退到 Noto Sans CJK SC / 思源黑体等中文字库。控件集中在右侧，未遮挡主城中央人物与广场。位置清单中的小数高度是精确等比结果，PNG 像素边缘由抗锯齿处理；客户端可以整体保持比例后按自己的像素对齐规则处理。

## 本地重建

从仓库根按 [v10 确定性重建流程](../../qdao_ui_style_recut_v10/README.md#确定性重建)执行。当前合成入口为 `node qdao_ui_style_recut_v10/tools/build_composites.mjs`，需要已有 Node.js / Sharp 及已生成的暂存通用件；它输出到 v10 暂存区，通过核验后再发布。

旧 `build.mjs` 已阻止直接写入，避免跳过当前来源匹配与验收。组合保持背景、人物和独立中文层，`hud_labels` 是本次明确保留的纯文字资源。

## 验证与接入边界

构建检查三张透明 PNG 的尺寸、RGBA 与 Alpha 范围，校验背景源 SHA-256 未变，并逐像素确认：**HUD 透明区域之外，完整预览与原背景的 RGB 像素完全相同**。检查结果记录在 `placement.json`。

完整 HUD PNG 已含中文，仅供静态预览或无需换字的展示。实际游戏接入应使用无文字皮肤层及原生标签，不能把原生标签叠到已有文字的 `hud_overlay.png` 上。按钮事件、可用性、焦点、悬停、触控热区及三个入口后的功能没有实现；不会据此声明已接入 Unity 或 FairyGUI。
