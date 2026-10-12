# 04 山岳守卫 · 当前交付状态

2026-10-05：**素材已完成；跑步60ms/帧、960ms/圈。** 196/196正式PNG、196份逐图来源、42份预览已同步。该时序来自本角色聊天用户的直接纠正，优先于共享文档/其他窗口旧75ms转述；仅本角色目录已更新。

| 动作 | 已完成范围 | 当前离线时序 |
|---|---|---|
| 跑步 run | N/NE/E/SE/S/SW/W/NW，各16，共128帧 | **60ms/帧，960ms/圈** |
| 受击 hit | E/W，各6，共12帧 | 40ms/帧，240ms/段 |
| 普攻 attack | E/W，各12，共24帧 | 30ms/帧，360ms/段；06帧起点150ms建议接触 |
| 施法 cast | E/W，各16，共32帧 | 45ms/帧，720ms/段；10帧起点405ms建议释放 |

本轮相对于provenance/audit/video_axis_baseline_delivery_20261004.json，替换30张跑步图，保留98张跑步与68张战斗图。旧轮“替换92张”属于此前历史，不能与本轮30张相加作为当前不同帧数量。完整槽位见MERGE_HANDOFF.md。

当前修复包含脚轴、抬脚侧甩、W上身视角连续和NW持杖臂连续。每个两帧位置段正常120ms；W实际可见支撑靴01–04/09–12在屏幕左前，05–08/13–16在屏幕右后。髋根遮挡，原01–08左/09–16右仅是相位意图，解剖侧标为未确认。

当前证据：

- 人工审核：provenance/audit/video_axis_final_visual_approval_20261005.json，绑定196张当前PNG SHA；分工人工观察后根复核，不据文件计数自动通过。
- 导出/迁移快照：provenance/audit/export_video_axis_precleanup_snapshot_20261005.json，30个本轮原生完整画布导出重现成功；166个保留图的历史删源证明通过。
- 清理：provenance/audit/video_axis_image_retention_20261005.json，56张项目中间图删除成功、失败0；用途分类名单独立保存。原用户视频和宿主生成图未动。
- 全量一致性：provenance/audit/final_delivery_verification.json，196张PNG/sidecar、42份预览、当前SHA及时长0错误，provenance中间图片剩余0。
- 播放器：provenance/audit/timing_960_player_validation.json，48/48项通过；正常960ms、0.5×1920ms、0.25×3840ms，战斗原时长保持。

[动画总览](preview/gallery.html) · [逐帧预览](preview/index.html)。浏览器已抽查正常、慢放及NW暂停/逐帧；该抽查不等同客户端实机验证。

配置目标为 GPT Image 2.5 Sunburst / max。使用内置 image_gen，实际附有本地身份画像、方向站姿、已确认画法和针对性动作参考。工具未提供 model/quality 选择器，也未返回实测型号/质量，因此实际提交与返回字段保持 null（未确认）。未使用收费 API/CLI。

本角色未接入客户端。历史布局点(512,928)不是实测物理地面，clientRootAnchor为null。世界位移、移速、停步/转向脚滑、碰撞及命中/释放事件需在接入时验证；离线观察不证明世界坐标锁脚。

本轮仅写本角色独占目录，未切分支、未暂存、提交或推送，未获取另一电脑未提交图。
