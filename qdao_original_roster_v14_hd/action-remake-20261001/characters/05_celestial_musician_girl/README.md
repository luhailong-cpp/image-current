# 05 天音少女 · 正式动作素材

2026-10-05：本轮素材修订已完成，交付196张1024×1024 RGBA透明PNG、14段动作。全部196帧已逐帧检查腿脚方向、自然屈膝承重和肩肘腕持琴；替换14张跑步脚轴及受击W03–05的远侧RIGHT手，共17张，保留114张正确跑步图和65张正确战斗图。正式替换、17张修图加载、14段正常播放和八方向160px跑步预览均已通过复验，见绑定当前图片SHA的[本轮收尾记录](provenance/foot-axis-20261004/closeout.json)。

[打开正式预览](preview/index.html) · [160px跑步检查](preview/timing-grounding-final.html) · [正式素材清单](final/manifest.json) · [接入交接](MERGE_HANDOFF.md)

| 动作 | 方向及帧数 | 正常播放 |
| --- | --- | --- |
| 跑步 | 八方向各16帧，共128张 | 60ms/帧，960ms/圈 |
| 受击 | E/W各6帧，共12张 | 40ms/帧，240ms/段 |
| 普攻 | E/W各12帧，共24张 | 30ms/帧，360ms/段 |
| 施法 | E/W各16帧，共32张 | 45ms/帧，720ms/段 |

跑步八方向均为01–08右脚支撑，09–16左脚支撑；前掌蹬地也计入接地。每个位置使用两张独立姿态：

| 接地位置 | 右脚 | 左脚 |
| --- | --- | --- |
| 前部落脚、接受负荷 | 01–02 | 09–10 |
| 身体经过支撑脚 | 03–04 | 11–12 |
| 髋下向后过渡 | 05–06 | 13–14 |
| 身体后侧前掌蹬地 | 07–08 | 15–16 |

全套共用0.65比例，各动作/方向整段共用固定源根，目标根(512,942)、底部原点pivot[0.5,0.080078125]，见[registration.json](registration.json)。保留自然屈膝、鞋尖俯仰和远近透视；脚轴跟随膝踝与动作方向，不把鞋机械画成屏幕竖直。没有逐帧移动贴地、重复帧、插帧或时长权重。解剖LEFT手扶琴上段、RIGHT手拨下弦，朝向切换不交换持手。

验收覆盖全部196帧静态实图，以及浏览器时序和疑点帧检查；结果和实际浏览范围见[验收](provenance/foot-axis-20261004/acceptance.json)与[浏览器记录](provenance/foot-axis-20261004/browser-check.json)。[收尾脚本](tools/closeout-axis-run.py)只有在17张替换全部验收、正式提升完成且浏览器记录与当前选图SHA一致后，才写入完成状态。客户端未接入实测，实际世界位移下的脚滑和速度匹配仍待验证。

逐项审查：[跑步脚轴 E/W](provenance/foot-axis-20261004/audit-EW.json)、[N/NE/SE](provenance/foot-axis-20261004/audit-NESEN.json)、[S/SW/NW](provenance/foot-axis-20261004/audit-SWNWS.json)、[跑步肩肘腕](provenance/foot-axis-20261004/audit-run-arms.json)、[受击](provenance/foot-axis-20261004/audit-hit.json)、[普攻](provenance/foot-axis-20261004/audit-attack.json)、[施法](provenance/foot-axis-20261004/audit-cast.json)。原问题审查保留修前SHA，修后以本轮验收及[提升记录](provenance/foot-axis-20261004/promotion.json)为准。

本轮修图使用宿主内置image_gen，目标GPT Image 2.5 Sunburst/max；工具实际型号与质量未披露，实际字段保留null。当前196个来源包含194个本批新绘来源和2个保留的旧来源，不能把全部来源重标为本轮生成。每张正式图片旁的`.png.generation.json`保存来源、原生尺寸、SHA、请求与返回证据和固定导出变换。[当前196帧提示词与来源汇总](provenance/foot-axis-20261004/selected-prompt-set.json)保留历史提示词缺失情况，不按当前配置补造旧记录。

成品与引用核验后，已清理140张原生、拒稿、诊断和导出中间图，本角色目录仅留196张正式游戏PNG和一张交付预览凭证；接入文件与逐图来源文字全部保留，见[本轮清理记录](provenance/foot-axis-20261004/cleanup.json)。清理后再次核验通过。历史图片路径只用于追溯，当前加载以`final/`为准。[文件核验](provenance/final-validation.json)。

2026-10-05时长更正：当前跑步为60ms/帧、16帧共960ms，每两帧接地位置占120ms。当前配置与预览已同步，历史验收中的75ms/1200ms只记录当时状态，见[时长更正记录](provenance/timing-60ms-20261005/change.json)。
