# 五行奇谈 · 组队 UI 重做 v2

2026-09-14：[Unity 官方 MCP 专用切图与客户端接入](unity-slices/README.md)。14 张原稿切片、透明边缘和九宫格已导入组队专用资源目录；本轮验收记录位于 unity-slices/qa。

2026-09-13。按用户要求改善组队界面清晰度，保留队伍成员与申请列表，删除“已同意”栏目。

- [实际客户端截图 · 2560](client-preview-2560.png) · [1920](client-preview-1920.png) · [四人申请列表](client-preview-compact-1920.png)。
- [新版效果图](team-ui-v2.png)：内置 image_gen 生成，原生 1931×814，未插值放大。
- [可交互预览](index.html)：使用独立原生文字、正式位图控件和人物头像，演示同意、拒绝、刷新与异常状态。
- [实际提示词](source/team-ui-v2.prompt.txt) · [生成记录](source/generation.json)。

## 布局与可读性

成员与申请同时可见。左侧成员采用横行，姓名、等级与门派紧密排列，队长／自己、在线／离线明确标记，空席降低强调。右侧申请保留头像、姓名、等级、门派，以及固定位置的同意、拒绝按钮。移除已同意记录；同意后申请从列表消失，成员名单更新。

标题保留国风书写气质，交互预览正文使用清晰中文无衬线字体。深玉绿、象牙米白、暖金、少量灯笼与结绳沿用项目指定风格；装饰集中在外围，为内容留出安静纸面。

效果图与交互预览是两种交付：前者展示完整手绘视觉，后者验证原生文字排布和交互。预览定向复用项目当前人物与控件，因此头像和细节不与生成整屏逐像素相同。

## 功能边界

2026-09-13 续作已完成：新版双栏界面已接入实际 Unity 客户端 `TeamWindow.cs`，并通过本轮 Unity 测试与截图验收。客户端使用权威快照，点击同意／拒绝只发送请求意图，成功回包后更新名单。当前工程尚无主城组队服务端 RPC，正式游戏继续显示服务未开放；没有加入模拟线上成功逻辑。HTML 预览和 Unity 离线预览采用固定示例数据，仅用于验证界面与交互。客户端最初通过 `client_ui_refresh_20260908/README.md` 定位，本轮按用户继续完成的要求更新组队窗口、对应测试和离线截图工具。

客户端实现与历史核查来源：

- `E:/work/mmorpg-client/Assets/Scripts/UI/Ugui/Team/TeamWindow.cs`
- `E:/work/mmorpg-client/Assets/Scripts/Game/Team/TeamUiState.cs`
- `E:/work/mmorpg-client/Docs/team-ui.md`
- `E:/work/mmorpg-client/.codex-artifacts/team-ui/members_2560x1080.png`
- `E:/work/mmorpg-client/.codex-artifacts/team-ui/applications_2560x1080.png`

已知原界面问题包括细楷正文、装饰重复、全身人物缩进头像框、空席文案重复，以及申请行内容距离过散。用户明确删除“已同意”的最新要求优先于旧三页合同。

## 本地打开

当前预览地址：http://127.0.0.1:4311/team-ui-v2/ 。需要重启时，在项目根目录运行：

```powershell
python -m http.server 4311 --bind 127.0.0.1 --directory designs
```

所有资源随本目录保存，无第三方在线依赖。生成质量以最高完成度为目标，内置工具未开放 model／quality 参数，未宣称强制设置 high。参考图因本次 Windows 沙箱读取故障，通过对话中的参考缩略图实际传入。

## 验收结果

已用本机 Edge 无头浏览器加载本地 HTTP 预览，检查 2560×1080、1920×1080 与 390×844：没有横向溢出、丢失图片、HTTP 错误或脚本异常，并实看桌面、手机及多页列表截图。

[布局报告](qa/layout-report.json) · [20项交互检查](qa/interaction-report.json) · [桌面截图](qa/preview-2560.png) · [手机截图](qa/preview-390.png)。交互验证覆盖同意后入队、拒绝、申请空态、满员仍可拒绝、队员权限、服务未连接、刷新锁定及反馈、申请和成员分页、末页删除后页码归位、Escape关闭与键盘重开。均为浏览器本地示例验证，不等于 Unity 或在线服务器验收。

### 客户端最终验收

Unity 6000.6.0f1：EditMode **27/27**、PlayMode **6/6** 全部通过。覆盖双栏显示、旧入口兼容、申请处理权限与快照、两侧独立分页、请求状态、输入阻挡与释放，以及真实 EventSystem 中的焦点恢复。

2560×1080、1920×1080 各十种状态，共 **20 张实际 Unity 渲染截图**；每张校验所有可见非空文字至少绘制一个字形，修复 Noto CJK 行高导致姓名整行被裁掉的问题，并实看双申请、紧凑申请、满员、空态、未连接、处理中和独立翻页样例。标题保留国风字体，正文使用随包且保留 OFL 授权的 Noto Sans SC。

[客户端验收记录及源码校验值](qa/client-integration-report.json) · [EditMode 原始报告](qa/client-editmode-tests.xml) · [PlayMode 原始报告](qa/client-playmode-tests.xml)。实际截图为生产 `TeamWindow` 加载离线示例快照；不表示线上服务器功能已经验收。
