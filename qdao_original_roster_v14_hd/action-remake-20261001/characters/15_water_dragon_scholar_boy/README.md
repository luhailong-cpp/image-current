# 15 水龙书生 · 修复版

196张正式PNG已导出并完成静态逐帧检查：八方向跑步128张、E/W受击12张、普攻24张、施法32张。跑步每圈960ms，每帧60ms，同一支撑足沿连续位置每两帧推进后换足。

- [完整预览](preview/all-directions.html)
- [单动作、慢放与逐帧](preview/index.html)
- [当前进度](STATUS.md)
- [合并交接、时序与剩余检查](MERGE_HANDOFF.md)
- [196帧精确路径及SHA](manifest.json)
- [当前静态复核](audit/current-static-review.json)
- [最新视频反馈修复及逐图SHA](audit/video-direction-20261004/repair-result.json)

最新版本动态播放观感尚未验收：自动浏览器读取本地file页面被安全策略拒绝；未绕过限制，不把旧通过结论沿用到新图。客户端未接入。

内置image_gen配置目标GPT Image 2.5 Sunburst / max，实际型号/质量未披露并逐图记录为未确认。只在本角色独占目录写入，保留旧图来源，未使用另一台电脑未提交素材。
