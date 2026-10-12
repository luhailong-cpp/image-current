> **当前入口（2026-10-09 最新覆盖）：只做主城、渔村、仙岛三张日景。春节、元宵、中秋元素自然混合穿插，不按节日分区，不再制作独立夜景或节庆套图。保留新画法与核心地标，向外扩建可走广场和道路；同图5000人分散活动仍是待验证目标。最终网格与总块数待定，正式单块仍4096×4096。** [当前制作](builtin_q64_production/parallel_20261005/README.md) · [权威范围](builtin_q64_production/parallel_20261005/production-scope.json)

> 其他13个地图制作线程已由root停止并归档，逐个只读核查均为inactive/notLoaded、最新回合interrupted，见[停止回执](builtin_q64_production/parallel_20261005/daylight-only-20261009/stopped-threads.json)。由当前root先做一张渔村日景扩建预览。02/03小镇继续取消。

> 下文及旧索引中的208／1280／1792、39／70等只作历史范围或来源统计，不是当前三图方案的进度、容量验收或客户端接入状态。

> **2026-10-05 历史并行开工快照：** 用户已确认[七套主城各一个独立任务并行制作](builtin_q64_production/parallel_20261005/README.md)，全部任务已实际创建，来源交接已就绪。[当前父任务源集](builtin_q64_production/resume_single_city_20260921/completion_20261004/current-work.json)为29个4K在制坐标，正式验收0、完整城市0；新产出以各任务记录为准。继续内置生图和GPT Image 2.5目标配置，不使用付费API。下文旧批次数量与旧单城优先安排均为历史快照。

> **2026-10-04 历史续作：** [天墉城节庆当前在制稿与来源](builtin_q64_production/resume_single_city_20260921/continuation_20261004/README.md)。本轮 7 次内置原生修补、恢复 1 张已有修补，更新 4 张 4K 在制稿；最新工作集合覆盖 11/256 个坐标，正式验收仍为 0，64K 整城未完成。下面的冻结数量和旧原生累计为历史检查点，续修请先读本入口。

> 2026-09-22 已按用户授权清理旧原图／回退图，最新保留范围及实际数量见[清理记录](cleanup-current-assets/README.md)。此前原生累计数字是历史生成记录，不表示清理后仍保留同等数量的原图。

> 用户要求移交新窗口继续。最新入口：[详细交接](主城美术详细交接-20260921.md)。本次冻结为天墉城节庆 8／256 个 4K 候选、正式验收 0；本窗口停止新增生图。以下历史检查点原样保留，当前文件及来源数量以交接快照和 session-state 为准。

> 2026-09-21 本窗口集中制作 **天墉城节庆** 一套。新增原生图、返修和未验收候选见 [本轮实时制作记录](builtin_q64_production/resume_single_city_20260921/session-state.json)；下文24块/502原生是接手时已合并批次快照，不包含该续作目录的新来源。正式64K交付仍为0套，客户端接入由另一窗口负责。

# 主城64K / 单块4K重制



2026-09 历史批次累计生成 **24个独立坐标的4096×4096局部候选**。**完整64K整城0/7套，正式验收0/1792块**。同一坐标的返修版本不重复计数。用户已确认继续全部主城至完成，维持原64K目标，无待确认的范围问题。



累计核验392张基础原生1254×1254细节图及110张原生返修图，保留原始字节和来源记录；正在制作的图块中已核验原图也计入源图数量。布局参考、预览和机械处理版本不计为新增原生图。高清细节采用分区生成、重叠拼接后裁成4K；没有将低清图直接放大冒充高清。小幅机械接缝配准会重采样边缘像素，位移与色彩校正另存记录。



[历史批次总览](builtin_q64_production/current-batch-overview.jpg) · [来源与数量核验](builtin_q64_production/current-batch.json) · [状态JSON](status.json)



| 外观 | 图块坐标 | 4K候选 | 检查记录 |

| --- | --- | --- | --- |

| 天墉城节庆 | r10_c07 | [无损PNG](builtin_q64_production/tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/output_v5/r10_c07.png) | [QA](builtin_q64_production/tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/qa_v5/visual-review-20260920.json) |

| 天墉城节庆 | r10_c08 | [无损PNG](builtin_q64_production/tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/output_v5/r10_c08.png) | [QA](builtin_q64_production/tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/qa_v5/visual-review-20260920.json) |

| 天墉城节庆 | r10_c09 | [无损PNG](builtin_q64_production/tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/output_v5/r10_c09.png) | [QA](builtin_q64_production/tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/qa_v5/visual-review-20260920.json) |

| 天墉城节庆 | r10_c10 | [无损PNG](builtin_q64_production/tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/output_v5/r10_c10.png) | [QA](builtin_q64_production/tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/qa_v5/visual-review-20260920.json) |

| 蓬莱仙岛日景 | r09_c10 | [无损PNG](builtin_q64_production/penglai_day/r09_c10_c11_c12_joint/output_v2_20260918/penglai_day_r09_c10_4k_joint_candidate_v2.png) | [QA](builtin_q64_production/penglai_day/r09_c10_c11_c12_joint/visual-review-v2-20260920.json) |

| 蓬莱仙岛中秋 | r09_c10 | [无损PNG](builtin_q64_production/penglai_mid_autumn/r09_c10_c11_c12_joint/output_v2_20260920/penglai_mid_autumn_r09_c10_4k_joint_candidate_v2.png) | [QA](builtin_q64_production/penglai_mid_autumn/r09_c10_c11_c12_joint/visual-review-v2-20260920.json) |

| 东海渔村·日景 | r08_c08 | [无损PNG](builtin_q64_production/donghai_day/r08_c08_c09_c10_joint/output_v3/r08_c08.png) | [QA](builtin_q64_production/donghai_batch_r08_c08_c10/resume_audit_20260918/visual-review.json) |

| 东海渔村·元宵 | r08_c08 | [无损PNG](builtin_q64_production/donghai_lantern/r08_c08_c09_c10_joint/output_v2/r08_c08.png) | [QA](builtin_q64_production/donghai_lantern/r08_c08_c09_c10_joint/output_v2/qa/visual-review-20260920.json) |

| 揽仙镇日景 | r08_c06 | [无损PNG](builtin_q64_production/lanxian_day/triple_r08_c06_c08/output_v2/r08_c06.png) | [QA](builtin_q64_production/lanxian_day/triple_r08_c06_c08/visual-review-v2.json) |

| 揽仙镇春节 | r08_c06 | [无损PNG](builtin_q64_production/lanxian_spring/triple_r08_c06_c08/output_v2/r08_c06.png) | [QA](builtin_q64_production/lanxian_spring/triple_r08_c06_c08/visual-review-v2-20260920.json) |

| 蓬莱仙岛日景 | r09_c11 | [无损PNG](builtin_q64_production/penglai_day/r09_c10_c11_c12_joint/output_v2_20260918/penglai_day_r09_c11_4k_joint_candidate_v2.png) | [QA](builtin_q64_production/penglai_day/r09_c10_c11_c12_joint/visual-review-v2-20260920.json) |

| 蓬莱仙岛中秋 | r09_c11 | [无损PNG](builtin_q64_production/penglai_mid_autumn/r09_c10_c11_c12_joint/output_v2_20260920/penglai_mid_autumn_r09_c11_4k_joint_candidate_v2.png) | [QA](builtin_q64_production/penglai_mid_autumn/r09_c10_c11_c12_joint/visual-review-v2-20260920.json) |

| 揽仙镇日景 | r08_c07 | [无损PNG](builtin_q64_production/lanxian_day/triple_r08_c06_c08/output_v2/r08_c07.png) | [QA](builtin_q64_production/lanxian_day/triple_r08_c06_c08/visual-review-v2.json) |

| 揽仙镇春节 | r08_c07 | [无损PNG](builtin_q64_production/lanxian_spring/triple_r08_c06_c08/output_v2/r08_c07.png) | [QA](builtin_q64_production/lanxian_spring/triple_r08_c06_c08/visual-review-v2-20260920.json) |

| 天墉城节庆 | r09_c07 | [无损PNG](builtin_q64_production/tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/output_v5/r09_c07.png) | [QA](builtin_q64_production/tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/qa_v5/visual-review-20260920.json) |

| 东海渔村·日景 | r08_c09 | [无损PNG](builtin_q64_production/donghai_day/r08_c08_c09_c10_joint/output_v3/r08_c09.png) | [QA](builtin_q64_production/donghai_batch_r08_c08_c10/resume_audit_20260918/visual-review.json) |

| 东海渔村·元宵 | r08_c09 | [无损PNG](builtin_q64_production/donghai_lantern/r08_c08_c09_c10_joint/output_v2/r08_c09.png) | [QA](builtin_q64_production/donghai_lantern/r08_c08_c09_c10_joint/output_v2/qa/visual-review-20260920.json) |

| 东海渔村·日景 | r08_c10 | [无损PNG](builtin_q64_production/donghai_day/r08_c08_c09_c10_joint/output_v3/r08_c10.png) | [QA](builtin_q64_production/donghai_batch_r08_c08_c10/resume_audit_20260918/visual-review.json) |

| 揽仙镇日景 | r08_c08 | [无损PNG](builtin_q64_production/lanxian_day/triple_r08_c06_c08/output_v2/r08_c08.png) | [QA](builtin_q64_production/lanxian_day/triple_r08_c06_c08/visual-review-v2.json) |

| 蓬莱仙岛日景 | r09_c12 | [无损PNG](builtin_q64_production/penglai_day/r09_c10_c11_c12_joint/output_v2_20260918/penglai_day_r09_c12_4k_joint_candidate_v2.png) | [QA](builtin_q64_production/penglai_day/r09_c10_c11_c12_joint/visual-review-v2-20260920.json) |

| 天墉城节庆 | r09_c08 | [无损PNG](builtin_q64_production/tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/output_v5/r09_c08.png) | [QA](builtin_q64_production/tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/qa_v5/visual-review-20260920.json) |

| 东海渔村·元宵 | r08_c10 | [无损PNG](builtin_q64_production/donghai_lantern/r08_c08_c09_c10_joint/output_v2/r08_c10.png) | [QA](builtin_q64_production/donghai_lantern/r08_c08_c09_c10_joint/output_v2/qa/visual-review-20260920.json) |

| 揽仙镇春节 | r08_c08 | [无损PNG](builtin_q64_production/lanxian_spring/triple_r08_c06_c08/output_v2/r08_c08.png) | [QA](builtin_q64_production/lanxian_spring/triple_r08_c06_c08/visual-review-v2-20260920.json) |

| 蓬莱仙岛中秋 | r09_c12 | [无损PNG](builtin_q64_production/penglai_mid_autumn/r09_c10_c11_c12_joint/output_v2_20260920/penglai_mid_autumn_r09_c12_4k_joint_candidate_v2.png) | [QA](builtin_q64_production/penglai_mid_autumn/r09_c10_c11_c12_joint/visual-review-v2-20260920.json) |



## 目标与制作状态



每套65536×65536、16×16块、每块4096×4096；7套共1792块。旧图和1254²整城参考只约束布局，不计为高清成品。按当前每块16张原生细节图的流程，全部基础细节需要28672张生成图，另需参考与接缝修复。当前仍在逐块制作，未完成总量。



## 路线与检查



后续生图从[统一模型配置](../config/image-generation.json)读取型号与画质，并遵循[模型策略](../docs/IMAGE_MODEL_POLICY.md)，优先使用内置image_gen；API备用路径仍需独立授权。已有图片的请求、实际型号与画质以对应来源记录为准，不能用当前配置回填历史；实际图片尺寸、来源与提示词逐张保存。



检查包括原像素细节、内部接缝和相邻图块衔接。节庆版应沿用同城结构。仍需完整外围邻接、导航对齐、独立前景、最近镜头、跨块移动与设备验收，尚未替换客户端地图，未发布生产manifest。



客户端按可见范围加周围一圈加载，目标外观齐备后整体切换；既有验证21/21通过、运行时代码编译0错误，见[客户端验证](E:/work/mmorpg-client/Docs/VerificationEvidence/city-tiles4k-atomic-20260917/summary.json)。客户端代码验证不代表新美术完成实机验收。



## 统一需求话术



所有主城地图按更Q版、圆润饱满、明亮干净的方向重制，使用内置GPT Image路线的最高可用画质。每套目标65536×65536，按16×16切成256张4096×4096图块；各区重新制作清晰细节，保持道路、建筑、台阶、水岸、出入口和镜头角度一致，重叠拼接后再裁切，逐条检查接缝。同城节庆版保持结构一致。客户端按视野加载并预载邻块。原生图、拼接图、切图清单和验收记录必须可追溯，未通过验收的不计为完成。



[主城地图切图规范](E:/work/image/主城地图切图规范.md)只规定主城切图和美术交付规则；客户端实现见[CityTiles4K](E:/work/mmorpg-client/Docs/CityTiles4K.md)。



## 保留的历史资料



- [七套Q版整城布局参考（1254²）](builtin_q64_all_city_references/README.md)

- [1792块离线坐标计划](q64_production_plans/README.md)

- [最初天墉Q版4K局部候选](builtin_q64_r10_c07/README.md)

- [旧4K试作](builtin_4x4/plan.json)、[32K密度试作](builtin_density32k_r05_c04/plan.json)

- [停用的GPT Image2.5 API执行包](q64_gpt25/执行包.md)，本轮不使用。

