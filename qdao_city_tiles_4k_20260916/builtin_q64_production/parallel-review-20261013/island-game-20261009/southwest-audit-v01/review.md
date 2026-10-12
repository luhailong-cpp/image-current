# 八仙岛西南区独立审计 v01

审计完成时间（UTC）：2026-10-13T04:48:37.513128+00:00。仅检查已有素材，无生图、AI 修图、生产目录写入、Git 操作或删除。

当前快照：49 个目标坐标；12 张完整 4096² 原生来源候选，8 张有可靠内部通过记录，4 张仍待修；已选 220/784 个 1024² 核心，缺 564 个。正式验收 0 张。

逐像素独立验证 12 张、201,326,592 像素，0 mismatch；原生来源图片与记录哈希全部匹配。派生 resolved 核心明确保留机械裁切来源，未将其记成新生图。

当前采用路径以 current-native-map.json 的 candidateArtifacts 为准，与 progress.currentAdopted4kFiles 一致。progress.currentCandidateByTile 的 r10_c04 指向旧版本，早期四块包和 README 不再代表当前采用组合；汇总指标 218 也落后于实际 220。

- 部分覆盖：r08_c02=12/16（仅第 2–4 子行）；r12_c03=15/16（只缺 s04_04）；r09_c06=1/16（仅 s01_01）。
- 北边：r08_c03、r08_c04 全覆盖但内部待修；r08_c02 首子行缺失；其余 r08 列为空。全区 c07 没有已采用核心。

已保存最新 r10–r11/c03–c04 四块 8192² 原生硬拼接，逐块复制验证 0 mismatch。预览明确标为缩放预览。此局部具有内部/共享边证据，外圈仍未验收，不能称为整区完成。

接缝结论：

- r08_c03 → r08_c04：geometry_pass。Four current native strips viewed; paving, low stone beam and blue/gold roof contours continuous; mild material variation retained.
- r08_c03 → r09_c03：geometry_pass。Four current native strips viewed; bamboo outlines, gold trim and roof courses continuous; painterly value variation remains.
- r08_c04 → r09_c04：needs_paired_material_review_or_repair。Four current native strips viewed; no newly identified large geometry gap. Earlier hash-bound south-edge material/highlight exceptions remain open; no prior rejection overridden.
- r09_c02 → r09_c03：geometry_pass_reused。c04-hardseam-west-r09c02-v01-review.json
- r09_c02 → r10_c02：geometry_pass_reused。c04-hardseam-west-r10c02-v01-review.json
- r09_c03 → r09_c04：geometry_pass_reused。connected-stepfoot-group-v01-root-review.json
- r09_c03 → r10_c03：geometry_pass_reused。connected-stepfoot-group-v01-root-review.json
- r09_c04 → r09_c05：needs_paired_source_repair。Four current native strips viewed; preserved 115px border strip retains abrupt leaf/material transition and a bright rectangular gold-frame patch at the guide boundary.
- r09_c04 → r10_c04：geometry_pass_reused。connected-stepfoot-group-v01-root-review.json; current r10c04 repair bbox affects only bottom115px and does not touch north edge
- r09_c05 → r10_c05：needs_paired_material_repair。Four current native strips viewed; wall cap retains a large soft patch around tile-local x2900..3400 near north boundary; adjacent paving/wall is sharp. Major geometry generally continuous.
- r10_c02 → r10_c03：geometry_pass_reused。c04-hardseam-west-r10c02-v01-review.json
- r10_c03 → r10_c04：geometry_pass_reused。connected-stepfoot-group-v01-root-review.json; current r10c04 lower roof repair bbox does not reach west edge
- r10_c03 → r11_c03：geometry_pass_reused。expansion-west-root-r11c03-review.json
- r10_c04 → r10_c05：needs_paired_geometry_repair。Four current native strips viewed; western low wall cap and inset bevel retain height/line mismatch in c05 local y1000..1650.
- r10_c04 → r11_c04：geometry_pass_reused。central-r11c04-resume-final-west-review.json; central-r11c04-pond-right-crisp-v02-west-supplement.json; current source-report inheritance and repair bounds verified
- r11_c03 → r11_c04：geometry_pass_reused。central-r11c04-resume-final-west-review.json; later right pond repair does not reach west edge

本轮实际查看 6 张 100% 接缝蒙版拼接（24 段）和 4 个 100% 四块交叉点。新检查的 r08_c03/r08_c04、r08_c03/r09_c03 轮廓连续；西侧粽叶交点、当前中央屋顶交点没有新增错接。东侧交点确认保留边带造成的金木框直线切换。

仍需修补：r08_c03 的砖缝/竹轮廓/地面解释；r08_c04 的模糊铺地、石梁切角、柱轮廓及地缝；r09_c02 的竹环/球面长折线与材质块；r10_c05 内嵌面板双线。外部 r09 c04/c05、r10 c04/c05、r09/r10 c05 及 r08/r09 c04 的具体全图坐标保存在 normalizedRepairQueue。后续生产由原制作窗口按最新根 AGENTS 执行：现有免费入口 2.5 优先，不可用可用内置 2.0；本独立审计没有调用生图。

参考记录：209 个直接核心记录共享同一布局及细节参考哈希，邮件风格记录分别指向原 PNG 与 JPEG；文件哈希不同，本审计未读取区外参考图，不推断二者像素等同。实际模型全部未确认，配置中的 2.5 不作实际型号证明。

最终复 hash：564 个快照输入，变更 0 个；输入稳定。

未完整覆盖坐标：

r08_c01, r08_c02, r08_c05, r08_c06, r08_c07, r09_c01, r09_c06, r09_c07, r10_c01, r10_c06, r10_c07, r11_c01, r11_c02, r11_c05, r11_c06, r11_c07, r12_c01, r12_c02, r12_c03, r12_c04, r12_c05, r12_c06, r12_c07, r13_c01, r13_c02, r13_c03, r13_c04, r13_c05, r13_c06, r13_c07, r14_c01, r14_c02, r14_c03, r14_c04, r14_c05, r14_c06, r14_c07

机器可读交付：inventory.json、assembly-review-manifest.json、final-rehash.json。文件均位于本独立审计目录。

坐标复核：220 个已选核心的记录坐标与 1024 核心/115 halo 网格一致，0 坐标冲突。十个 resolved 核心的机械裁切上游记录已另存于 derivedSelectedCoreProvenance。

已重读用户 2026-10-13 最新根指令。原制作窗口已恢复；本报告为固定输入快照审核，不取代原制作 progress，也不声明全项目暂停。
