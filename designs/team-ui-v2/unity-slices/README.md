# 组队 UI · Unity 官方 MCP 切图

来源为已完成的 `../team-ui-v2.png`（原生 1931 × 814）。本轮通过 Unity 官方 relay 的 `Unity_RunCommand` 在 Unity 6000.6.0f1 中切图、写入 PNG 并配置 Sprite 导入器。没有重新生图。

14 张正式 PNG 位于 `png/`，同步到客户端 `Assets/Resources/UI/Ugui/TeamV2/`。切片包含主框、主标题牌、分栏标题牌、成员行、申请卡、两个动作按钮、关闭钮、头像边框、空位圆标、两枚身份徽章和两枚在线状态点。总计约 0.9 MB。

`manifest.json` 记录原稿哈希、原生尺寸、裁剪坐标、处理方式、资源路径、Unity GUID、九宫格边距与逐图 SHA-256。无字底板由原稿干净纸面/玉面及原始边缘重建；原稿中的玩家资料与按钮文字不进入底图，运行时由 TMP 渲染。圆框、关闭钮、空位和状态点使用真实透明 Alpha。

导入为单张 Sprite / FullRect / 100 PPU，关闭 mipmap、保持原生尺寸、Bilinear / Clamp / Uncompressed。带边距的控件由 uGUI `Image.Type.Sliced` 拉伸；圆形图标保持比例。仅既有灯笼和短流苏复用当前共享资源。

## 客户端

- `Assets/Scripts/UI/Ugui/Team/TeamUiArt.cs` 独立加载本轮切片。
- `Assets/Scripts/UI/Ugui/Team/TeamWindow.cs` 使用原稿双栏结构：五条成员行、两条宽申请卡或四条紧凑申请行、独立分页、同意/拒绝/刷新及关闭。
- 原有主城「组队 [T]」和 T / Escape 行为继续使用。正文沿用 Noto Sans SC，标题保持国风字形。
- 权威快照、队长权限、满员限制、请求锁定、超时和焦点恢复继续沿用原逻辑。当前服务端尚无主城组队 RPC，正式游戏会显示未开放；测试里的固定示例角色只用于离线验证。

## 复现

在目标工程 Unity 编辑器的稳定编辑模式下，使用已配置的官方 relay 先执行 `tools/SliceTeamUi.cs`，再执行 `tools/CleanTitleAlpha.cs` 清除主标题外围与透明区相连的天空残色。`tools/mcp-call.mjs` 是 stdio JSON-RPC 调用器，调用格式为 `node tools/mcp-call.mjs request.json <editor-pid>`，需提供当前编辑器进程 ID；它使用官方支持的 `--instance-id` 避免匹配历史编辑器登记。

`tools/mcp-slice-result.json` 和 `tools/mcp-title-alpha-result.json` 保存成功的官方 MCP 响应。`tools/inspect-assets.py` 只读核对原稿、导入 PNG 与 Sprite 元数据，并生成完整清单；适用于核验资源是否被后续任务更改。

实际渲染与测试证据见 `qa/`；本轮最终验证范围和结果见 `qa/validation.json`。切图检查拼图见 `contact-sheet.png`。