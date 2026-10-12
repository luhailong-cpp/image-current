# 00 跑步脚向独立静态复核与 SE 定向修复

依据用户最新要求独立看鞋掌长轴、膝踝衔接与跑向；月影07不作为已通过模板。逐帧输入SHA及64帧判断在 foot-direction-audit.json，原选表快照在 source-snapshot.json。

- E：16帧未见明确鞋掌向外扭，保留。后腿屈膝足尖下垂不能按脚尖屏幕位置误判外八。
- S：保留。03–08与11–16抬脚有轻微斜鞋底/外偏观察，但静态证据不足以认定与跑向相反，不扩大为必须重画。
- SW：16帧保留。08–12放大后鞋尖实际仍向左下；16-v3保留。
- SE：原01、02、11–16屏幕左侧前鞋明显朝左，与右下跑向冲突。01/02由root处理；本代理完成11–16。

## 推荐交接

| 帧 | 原生推荐 | SHA256 |
|---|---|---|
| 11 | generation/run/SE/11-v3.png | 7a666f95bb60ad680dd33f122dbacc035152b7abdbe55854f5684b110062c14d |
| 12 | generation/run/SE/12-v4.png | 19326f7c70e03b069034c52c86c8af3fefd2a24f87b39b81c4ab347082a8e163 |
| 13 | generation/run/SE/13-v3.png | 05395e6489b36f083d7b0939c797c469c41b5f444a34d3924b12094c84ee8a6b |
| 14 | generation/run/SE/14-v2.png | 2b07525c4aac897d8625ed601b74afdff3abaa760e7cd88eb5191eadf56babee |
| 15 | generation/run/SE/15-v3.png | 2b83bc14991eeb4489687dbdcba5e7d503137e4adcacf867de240643c2925194 |
| 16 | generation/run/SE/16-v2.png | f38691f64204352ac149cc3956c78eca43f32e54c68b5d90b0789ed3c76a870e |

六张均1254×1254透明RGBA，逐图prompt/request/receipt/png.generation.json齐全。实际型号与质量未披露，均null；配置目标单独保存。12-v3改错脚，拒用；12-v4已修正。

本轮实际看图可见鞋头转到踝部右下，未见继续向左外翻、断踝或多脚；各自身姿态与上身保留。原生图未做程序缩放、贴地、镜像或平移。

前后对照：SE-11-13-before-after.jpg、SE-14-16-before-after.jpg；完整原生画布联系表：SE-recommended-full-canvas.jpg。联系表仅作诊断均匀缩放，来源记录齐全。

仅为静态推荐，未改selected-new、manifest或导出。720ms为主比较语境，本轮没有实时播放或客户端接地验收；相位/接地/根点连续性仍须总控检查，不能据此宣称动作全部通过。
