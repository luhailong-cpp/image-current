# 五行奇谈 · 群组、世界频道与谣言

2026-09-14。补齐三项社交 UI，使用与邮件一致的道家 Q 版玉绿、象牙米白、暖金手绘风格。

## 直接查看

| 页面 | 内置生图效果图 | 可点击预览 |
|---|---|---|
| 群组 | [群列表、聊天与群资料](01-groups.png) | [打开群组](http://localhost:4351/social-ui-v1/index.html?view=groups) |
| 世界频道 | [聊天、坐标与物品分享](02-world.png) | [打开世界](http://localhost:4351/social-ui-v1/index.html?view=world) |
| 谣言 | [只读系统传闻与事件](03-rumor.png) | [打开谣言](http://localhost:4351/social-ui-v1/index.html?view=rumor) |

[本地入口文件](index.html) · [三页布局和状态规格](UI_SPEC.md) · [邮件 UI](../mail-ui-v1/README.md)。

## 已完成的功能

**群组**：群列表、搜索、未读、群聊天、群公告、成员与在线状态、群主标记、创建群组、邀请好友、编辑本人作为群主的群名和公告、置顶、消息提醒、退出确认；手机群列表/聊天/资料分层显示。未发送的草稿按群组保存，切到世界再回来仍保留。

**世界频道**：当前、世界、帮派、队伍四个独立消息记录与草稿；昵称、等级、Q 版头像、左右聊天气泡、原生输入、表情文字、分享卡、人物资料、物品和坐标详情。空白不可发送，中文输入法组合期间不误发送，Enter发送、Shift+Enter换行。阅读旧消息时保持位置，通过新消息提示回到最新。

**谣言**：只读系统传闻，无聊天输入框；全部/妖兽现世/珍宝奇遇/仙友捷报分类、搜索、无结果空态、事件详情、位置与物品信息、倒计时和到时状态、频道时刻与回到最新。计时结束后正文与状态保持一致。

页面外的“设计预览”提供重置和本地新消息演示，社交窗口内保留游戏内容与操作。

## 美术和素材

三张整屏原画均为内置 image_gen 输出，原生 **1931×814**，未插值放大。目标游戏布局为 **2560×1080**。项目指定风格图是唯一美术定调；用户截图仅提供群组、聊天和系统传闻的功能参考。

- [群组提示词](prompts/01-groups.prompt.txt)
- [世界频道提示词](prompts/02-world.prompt.txt)
- [谣言提示词](prompts/03-rumor.prompt.txt)
- [实际生成记录与校验值](source/generation.json)
- [复用素材及精确来源](asset-manifest.json)（原网页22张，原生聊天另复用1张纸色底纹）

保持太极、葫芦、圆润云纹、直发/束发的不同 Q 版角色、青绿仙山和玉瓦道观，桂枝、暖灯与短红穗局部点缀。交互预览由独立位图皮肤与原生文字组合，与整屏原画不逐像素相同。模型与质量使用宿主实际工具能力；工具没有 model/quality 显式参数，未宣称强制设置 high，也未调用外部收费 API。

## 验收

群组 **28 项**、世界/谣言 **65 项**定向检查通过，报告中无浏览器异常或失败资源。覆盖 **2560×1080、1920×1080、390×844**。群组跨页草稿另用一项定向检查验证，不为此重复重做已通过的截图。

[群组报告](qa/groups-validation.json) · [世界与谣言报告](qa/channels-validation.json)。

| 实际浏览器画面 | 截图 |
|---|---|
| 群组三栏 | [2560](screenshots/01-groups-2560.png) · [1920](screenshots/04-groups-1920.png) |
| 群资料、邀请 | [群资料](screenshots/02-group-info-dialog.png) · [邀请好友](screenshots/03-group-invite-dialog.png) |
| 手机群组 | [列表](screenshots/05-mobile-groups.png) · [群聊](screenshots/06-mobile-group-chat.png) · [群资料](screenshots/07-mobile-group-info.png) |
| 世界频道 | [2560](screenshots/channel-world-2560.png) · [1920](screenshots/channel-world-1920.png) · [手机](screenshots/channel-world-390.png) |
| 谣言 | [2560](screenshots/channel-rumor-2560.png) · [1920](screenshots/channel-rumor-1920.png) · [手机](screenshots/channel-rumor-390.png) |

需要重启预览时，在项目根目录运行：

```powershell
python -m http.server 4351 --bind 127.0.0.1 --directory designs
```

复验脚本为 [groups-smoke.cjs](qa/groups-smoke.cjs) 和 [channels-smoke.cjs](qa/channels-smoke.cjs)，使用本机已有 Playwright/Edge。

## 交付范围

三页效果图和网页原型保留。2026-09-16 已新增 Unity 原生群组、世界与谣言窗口，正式主城入口为“仙友会 [C]”，并提供独立离线预览。世界文本聊天已编写现有 RPC 适配；当前服务端只开放 World/Private，界面只接 World，其他频道清晰显示未开放。群名、人物称呼、消息、事件和数值均为离线样例，不发给真实玩家，也不发放奖励或调用寻路。详见 [Unity 交付](unity-slices/README.md) 与客户端 `Docs/SocialUI.md`，实际联机效果仍需实服联调。
