# 五行奇谈 · 人物与宝宝属性 UI 重绘

2026-09-09。按用户补充的选角参考图提取 UI 皮肤，保留最初人物/宝宝加点截图的信息布局。

- [人物 UI 原图](01-character-ui-no-affinity.png)：已去除“相性点”页签，保留六项属性、方案切换、四行加点滑杆、属性/加点/技能页签。
- [宝宝 UI 原图](02-pet-ui.png)：四只宝宝列表、六项属性、两列加点控件、洗点/抗性等按钮。
- [两图切换预览](index.html)：静态视觉稿，面板内部按钮不执行游戏操作。
- 提示词：[人物](character-ui.prompt.txt)、[宝宝](pet-ui.prompt.txt)。

采用米白纸面、深玉绿标题与主要控件、细金边和云纹装饰。用户明确“要 UI 风格”后，取消大场景与全身人物的展示方向，以属性窗口为主体。较早的 `character.prompt.txt` 是未采用的场景方向提示词，不属于最终版。

两图使用宿主内置 `image_gen` 生成，原始 PNG 原样保存，实际像素尺寸和来源见 [manifest.json](manifest.json)。工具未提供可设置/核验的 model、quality 参数，本次没有显式强制 `gpt-image-2` 或 `high`，也未切换到付费 API/CLI。

Windows 文件读取接口存在 ACL 故障，因此通过会话内显示的参考图副本传入生成工具。项目中保留原始风格与布局参考。图片中的文字和数字已烘焙，仅作为历史 UI 美术效果稿。当前无字控件改由 [v10 统一风格重切](../../../qdao_ui_style_recut_v10/README.md)交付，31 张属性切片见 [切片说明](unity-slices/README.md)。本页静态预览与旧版可交互预览保持原样，未同步 v10 皮肤。并行客户端任务已导入 31 张 v10 属性切片，并完成 [人物／宝宝面板 Unity 编辑器验收](unity-slices/unity-validation-v10.json)：26 项测试通过、0 项失败；使用离线样例数据，未验证在线服务器。

本次局部修订：[去除相性点提示词](character-remove-affinity.prompt.txt)。[修订前人物图](01-character-ui.png)保留供追溯；当前预览及下载已切换到无相性版本。
