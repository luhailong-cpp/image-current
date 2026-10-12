# 八仙岛西南区：当前可读取交付

本轮完成 r09_c03、r09_c04、r10_c03、r10_c04 四张 4096×4096 原生拼接候选，以及一张 8192×8192 连续拼图。四块内部检查、组内全部横纵共享边和四块交点检查通过。逐像素来源核验共 67,108,864 像素，0 mismatch；没有放大、羽化、变形或调色。局部自然笔触/材质调子差见 QA 记录。

交付入口为 [manifest.json](output/contiguous-r09-r10-c03-c04-v01/manifest.json)，[连续8192图](output/contiguous-r09-r10-c03-c04-v01/r09-r10-c03-c04-native-8192.png)，[2048预览](output/contiguous-r09-r10-c03-c04-v01/preview-2048.png)。同目录包含四张4K图、每图source-ID掩码、来源报告和派生记录。

准确数量：4张候选、4张内部通过、4张组内共享边通过；8条组外图块边仍需邻块生成后检查，完整外缘通过0张、正式验收0张。西南分区总49张，剩45张未生成；本组不代表全区或整图完成。

本轮将粽叶/绳结、墙脚、台阶、庭院铺地、石栏、金肋和三段金色屋顶修补合入。完整组检查额外发现台阶下方断砖缝，已通过扩大已有原生修补选择范围修好。最终组合规格在 [connected-stepfoot-v01-spec.json](qa/connected-stepfoot-v01-spec.json)，最终根检查在 [root-review](qa/connected-stepfoot-group-v01-root-review.json)。旧候选和旧误通过记录保留，仅当前manifest为交付入口。

主控于2026-10-11报告生图网络权限撤销，要求本地续做并等待恢复。本窗口未反复重试网络，也未换入口/账号或付费API。所有当前可执行的拼接、检查、导出已完成。剩余坐标、8条外缘和阻塞见 [local-continuation-20261011.json](local-continuation-20261011.json)。恢复后从当前导出边界约束继续，勿重复生成本组。

每次内置生图的精确prompt、参考角色/hash、坐标、实测1254²尺寸、回执和源hash在 prompts、guides、receipts、native 中。最终每个像素按来源报告和source-ID掩码可追溯；16格基础数组不能单独重现修补后的成品。实际model/quality工具未披露，记录为null。

仅本区可写。日景Q版道家春节风格和既有地图布局继续有效。仅允许内置image_gen；实际游戏、Unity、容量运行测试不在本次范围，旧AGENTS要求已撤销。历史README保存在qa/README-before-connected-group-20261011.txt，仅供历史追溯。
