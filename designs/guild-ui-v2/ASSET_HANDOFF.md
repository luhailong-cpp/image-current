# 帮会 UI 资源合同

2026-09-14 更新：全部 27 张正式切图已通过 Unity 官方 relay MCP 导入客户端，原有 GUID 和源像素保持；当前接入及 28 项测试结果见 [最新记录](official-mcp-client-20260914.json)。下文保留初次复制及 9 张资源接入的历史说明，九宫格和原尺寸合同继续有效。

2026-09-13。此包供 `designs/guild-ui-v2` 自包含浏览器演示使用。27 张界面图片与 2 张参考图全部从仓库现有已验收素材原字节复制；未调用生图，未改色、重裁、重采样或绘制新控件。逐文件来源、SHA-256、原始尺寸、像素模式与伸缩约定见 [asset-manifest.json](asset-manifest.json)。目的文件与来源文件 SHA-256 全部相等。

风格依据 [UI 制作规范第 2 节](../../qdao_ui_redesign_v5/UI_SPEC.md#2-统一视觉与控件层级)：道家 Q 版手绘，深玉绿、象牙米白、暖金；灯笼、朱红短穗仅作节庆点缀。`source/reference-style.png` 是指定风格图，画中历史服名、角色与其他文案不作为本界面的业务数据。`source/guild-overview.png` 是此前生成的帮会总览静态参考，不作为动态 UI 整屏背景。

## 控件与伸缩

以下数值顺序固定为 **左／上／右／下**，单位是原始 PNG 像素，直接读取属性 v10 正式清单 `destinationBordersLeftTopRightBottom`。禁止将 Unity 的左／下／右／上顺序直接用于 CSS。

| 图片 | 原尺寸 | 九宫格 L/T/R/B |
|---|---:|---|
| `window_frame.png` | 1546×743 | 97 / 99 / 97 / 74 |
| `button_primary.png` | 376×97 | 66 / 30 / 66 / 30 |
| `button_secondary.png` | 271×82 | 30 / 27 / 30 / 27 |
| `tab_horizontal.png` | 279×71 | 27 / 24 / 27 / 24 |
| `stat_field.png` | 273×62 | 12 / 12 / 12 / 12 |
| `portrait_frame.png` | 134×115 | 11 / 11 / 11 / 11 |

九宫格只伸缩中心与相应边段，圆角和边饰按一致比例缩放；显示尺寸不能使固定边距互相挤压。标题牌 `title_plate.png`、关闭钮 `close_button.png`、短穗 `close_tassel.png`、公告图标 `notice_icon.png`、灯笼 `lantern.png`、所有圆徽章和头像仅等比显示。清单中九宫格为 `null` 代表没有可伸缩合同。

功能徽章：`round_badge_taiji.png`、`round_badge_furnace.png`、`round_badge_sword.png`、`round_badge_lotus.png`、`round_badge_pagoda.png`、`round_badge_mountain.png`、`round_badge_compass.png`。保留透明边缘；不得把圆徽章横向拉成长按钮。

## 头像与商品

| 本包图片 | 原团队资源 | 演示用途 |
|---|---|---|
| `avatar-1.png` | `24_lu_dongbin.png` | 吕洞宾头像 |
| `avatar-2.png` | `25_lion_drum_guard.png` | 狮鼓卫头像 |
| `avatar-3.png` | `27_ink_kite_ranger.png` | 墨鸢游侠头像 |
| `avatar-4.png` | `29_he_xiangu.png` | 何仙姑头像 |
| `avatar-5.png` | `30_han_xiangzi.png` | 韩湘子头像 |
| `icon-pill.png` | `018_medicine_gourd_flask.png` | 丹药商品的药葫芦徽记 |
| `icon-scroll.png` | `071_scripture_scroll.png` | 经卷徽记 |
| `icon-talisman.png` | `038_talisman_scroll.png` | 符箓徽记 |
| `icon-chest.png` | `round_badge_pagoda.png` | 宝物通用徽记；当前并非专门宝匣插画 |

头像直接沿用 `designs/team-ui-v2/assets`，仅重命名。头像裁切由显示层 `object-fit`／遮罩处理，不改源图。角色形象与游戏内成员身份映射属于演示数据，不表示生产账号归属。商品名称、价格、库存与奖励由独立原生文字和数据表达，不从徽记推导数值。

## 原生文字与接入边界

帮会名、等级、成员名、职位、在线状态、公告、贡献、货币、页签标题和按钮标签由 HTML／实际客户端原生文本叠加；这些控件皮肤没有烘焙动态文案。文字位于装饰之上，流苏和灯笼不占点击区域。选中、禁用、加载和失败状态须有可读文字或形状标志；焦点、可访问名称与事件由程序负责，图片本身不提供交互。

资源复制阶段仅制作本目录浏览器资源包；随后已另行接入 `E:/work/mmorpg-client` 的 Unity 帮会 UI。实际客户端同步了其中9张图片，并复用工程已有的窗口、按钮与页签皮肤，保留源图片字节和九宫格合同。客户端入口、协议边界、资源校验与独立验收见 [client-integration.json](client-integration.json)。浏览器测试和源属性切片的历史 Unity 验收不能替代本次帮会页面的客户端验证；本次未进行线上服务器验收。
