# 邮件 · Unity 素材与原生接入

2026-09-16。项目指定的道家 Q 版风格：深玉绿、象牙纸色、暖金，配合太极、葫芦与少量节庆装饰。

## 素材

本包复用已经确认的独立 PNG；没有把整张界面效果图作为可交互窗口，也没有再次插值放大或重绘。标题、正文、群名、消息、附件数量与控件状态由原生 TMP/uGUI 生成。

- **19 张原生 Sprite**：`Assets/Resources/UI/Ugui/MailV1/`。
- [源文件清单](input-manifest.json)：原 PNG、SHA-256、尺寸、九宫格边距来源。
- [Unity 导入清单](manifest.json)：实际 GUID、资源键、原生尺寸与边距。
- 源 PNG 保留在 [assets](../assets/)；资源名沿用原文件名。
- Unity **6000.6.0f1**；Single Sprite、Full Rect、100 PPU、无 Mipmap、Clamp、Bilinear、Uncompressed；保留输入 Alpha 和原生尺寸。
- 窗框与按钮的边距经过原 PNG SHA-256 比对，沿用已有客户端导入契约。活动图、头像和装饰不作为九宫格拉伸。

导入器位于客户端 `Assets/Editor/MailSocial/MailSocialAssetImport.cs`。编辑模式菜单：`MMORPG / UI / Import approved mail and social sprites`。导入前检查全部源哈希；重导入保留已有 GUID。

整屏原画是美术目标，原生窗口采用独立素材组合；不会声称两者逐像素相同。
