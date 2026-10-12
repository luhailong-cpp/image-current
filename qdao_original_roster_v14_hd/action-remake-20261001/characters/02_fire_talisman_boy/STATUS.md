# 02 火符少年当前进度

2026-10-05：本轮196张全部动作、全部方向手脚重新看图复核完成。局部重画13张，保留183张；本轮替换槽位：run/E/03、run/E/04、run/E/11、run/E/12、cast/E/04、run/N/01、run/N/02、run/N/03、run/N/04、run/N/09、run/N/10、run/W/03、run/W/11。

检查肩—肘—腕—握柄的连接、解剖右手五张红符扇与左手单铜铃，及髋—膝—踝—鞋头的运动平面；保留自然屈膝、重量转移和透视。完整逐帧当前SHA与结论见reviews/full-limb-final-20261005.json，14组动作的正常/慢放浏览器抽样及控件检查见reviews/full-limb-browser-20261005.json。文件数和SHA不代替美术判断。

共196张1024×1024 RGBA正式PNG：跑步128、受击12、普攻24、施法32。跑步正常16×60ms=960ms、慢放3840ms，同一支撑脚每个相对位置两张独立姿态；按2026-10-05本聊天最新用户要求采用60ms，覆盖旧75ms。受击240ms、普攻360ms、施法720ms保持。逐图来源与导出像素审计另见reviews/full-source-chain-audit.json。

上一轮2026-10-04视频脚轴修订曾替换25张跑步；其历史报告保留，新一轮以full-limb-final-20261005.json的196张SHA为准。

交付：previews/index.html（四动作）、previews/run-grounding.html（八向跑步）、MERGE_HANDOFF.md、MERGE_FILES.csv。正式游戏图在frames/，仅修改本角色目录，未操作共享Git暂存/提交/推送。

本批使用内置image_gen，目标GPT Image 2.5 Sunburst/max；工具未开放型号/质量选择器且未披露实际值，逐图记未确认。没有收费API/CLI调用。

客户端尚未接入，游戏内滑步、位移、根点、碰撞与事件同步未验。此前过程图批量清理被自动审批以“blocked by policy”拒绝，未给具体理由；过程图暂留，未绕过重试，见reviews/cleanup-blocked.json。
