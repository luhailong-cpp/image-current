# 00 金发带道童当前状态

> 当前交付：60ms/帧，16帧共960ms；相邻位置两帧共120ms，¼慢放3840ms/圈。196张图片内容和68帧战斗时序保持不变。此前75ms/1200ms记录为历史；当前以 run-timing.json、manifest 与预览为准。
> 2026-10-05全动作复核：196帧完成静态检查，本轮补修W03/W11与NE04/NE12摆臂经过位、SW06悬空腿经过位。五张已合入正式导出；跑步16×75ms=1200ms。相邻落脚位置各两帧依次推进。动态及客户端仍未验收。详见[本轮完整记录](review/full-body-20261004/summary.json)。

> 2026-10-04最新：八方向跑步128帧接地与手脚修订已合入196张导出；落脚位置依次推进，各相邻位置两张独立姿态，正常16×60ms=960ms。逐图及独立静态复核完成；实际动态与客户端未验收。当前交付见[DELIVERY.md](DELIVERY.md)。

196张资源已落盘：八方向跑步128帧，E/W受击12帧、普攻24帧、施法32帧。当前以四个相邻位置各两帧的完整原生选表为准；旧14槽脚向修订记录仅为历史。

<!-- CURRENT_SNAPSHOT_START -->
核对时间：2026-10-05T04:54:41.818698-04:00（America/New_York）。本段由 tools/audit_provenance.py 实扫更新。

当前候选导出 **196/196**，缺 **0** 槽；本批本角色 generation 已关联原生生成记录的原图 **145** 张，另排除 **0** 张无原生记录或派生 PNG。正式美术通过 **0**；客户端 **未接入、未运行**。

| 动作/方向 | 实际导出帧号 | 缺失帧号 | 帧时长 / 完整段时长 |
| --- | --- | --- | --- |
| run/N | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 无 | 60 / 960 ms |
| run/NE | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 无 | 60 / 960 ms |
| run/E | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 无 | 60 / 960 ms |
| run/SE | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 无 | 60 / 960 ms |
| run/S | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 无 | 60 / 960 ms |
| run/SW | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 无 | 60 / 960 ms |
| run/W | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 无 | 60 / 960 ms |
| run/NW | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 无 | 60 / 960 ms |
| hit/E | 01、02、03、04、05、06 | 无 | 40 / 240 ms |
| hit/W | 01、02、03、04、05、06 | 无 | 40 / 240 ms |
| attack/E | 01、02、03、04、05、06、07、08、09、10、11、12 | 无 | 30 / 360 ms |
| attack/W | 01、02、03、04、05、06、07、08、09、10、11、12 | 无 | 30 / 360 ms |
| cast/E | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 无 | 45 / 720 ms |
| cast/W | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 无 | 45 / 720 ms |

逐图原生PNG、导出对应、完整SHA、配置/回执证据见 [来源审计](review/provenance-completion.json) 的 generationInventory 与 frameInventory。派生联系表单列 excludedGenerationPngs，不计作原生素材。

跑步当前八方向统一960ms/圈，16帧各60ms；正式预览仅保留正常、慢放、暂停与逐帧，旧快档和旧权重已退出当前配置。客户端速度与滑步未验证。

已确认失败请求 11 项（原始网络错误证据保留）；无完成证据请求 13 项（unknown，不等同于已确认失败）。

- `generation/combat/attack/W/03-v2.request.json` — `confirmed_failure`；SHA `741a1d4b9b5cfc0f9b1444db3f88538c1865026f8e7d56ec70bb1ecb4768f5e1`。
- `generation/combat/attack/W/06-v1.request.json` — `confirmed_failure`；SHA `46b18acd30cdc2e76aab1eb552faa90e3a9cefb054396a9ba700a871a8f424ab`。
- `generation/combat/attack/W/06-v2.request.json` — `confirmed_failure`；SHA `15f79062b2d44e7fca1cdbd8b10929ed62b80bda705b618c82ab3c164fde5fb2`。
- `generation/combat/attack/W/09-v2.request.json` — `confirmed_failure`；SHA `9183a04c7884b896fac3b598ab907eaa9dc5e5f4bed12d1ecffe02bfdbbd6509`。
- `generation/combat/attack/W/12-v2.request.json` — `confirmed_failure`；SHA `79ae4b2bf72be796de06deb7ce2a84cc93222ac6b0009cbd267927ee1a935fa0`。
- `generation/combat/cast/W/16-v1.request.json` — `confirmed_failure`；SHA `5a4f35dbfa78cba8797b994877eb7d284b61a8330c1b5194e223d22232b5209e`。
- `generation/combat/cast/W/16-v2.request.json` — `confirmed_failure`；SHA `fd301a6b0279b4605f81bdf5d0d375e3d524243abf3cf044a7699b86ebec4d12`。
- `generation/combat/cast/W/16-v3.request.json` — `confirmed_failure`；SHA `5d13252494f0ca7d776eece32b29a35e01f57aa5ffbec9dab5efc6ca81df8fa0`。
- `generation/run/E/05-v1.request.json` — `confirmed_failure`；SHA `46747f7020615f015c38ab842a3c5c62d384e7102ddffe23d8a897cc92c00078`。
- `generation/run/N/01-v1.request.json` — `confirmed_failure`；SHA `4369161b44a6161fc9f1b1c1ffcd092d42851e587181ed1261f72a668bd045c5`。
- `generation/run/N/01-v2.request.json` — `confirmed_failure`；SHA `cb1890b901b4b6b3ec504771eeb236648b3c9a4100c0ceb8349269f5ce8fe0b5`。
- `generation/combat/attack/W/03-v1.request.json` — `unknown_no_completion_receipt`；SHA `96320572328a224d40ecb4b8f5e4af4b8a14d74d512d1a7c88d3c370cf0ba020`。
- `generation/combat/attack/W/05-v1.request.json` — `unknown_no_completion_receipt`；SHA `2f079c5037e7d3ec3ed3c4a27785f6b847804003723e86cf0c0e3e182ee63218`。
- `generation/combat/attack/W/07-v1.request.json` — `unknown_no_completion_receipt`；SHA `8d2016feaa587d58e776fd6cc7eb63afa451e16d29b4c07f0b11dba700fd9b42`。
- `generation/combat/attack/W/08-v1.request.json` — `unknown_no_completion_receipt`；SHA `a1c1008c811243aa28036ffabf6711968d29c6541512d24205ea39cf48f84f15`。
- `generation/combat/attack/W/09-v1.request.json` — `unknown_no_completion_receipt`；SHA `507432333aaec1966a93262c900b54494c6b92d3bd8f91615e72a22905f3bcca`。
- `generation/combat/attack/W/10-v1.request.json` — `unknown_no_completion_receipt`；SHA `b68dee70bd0859527b63a427f88fcb32419e468eb11f248d3b0f41e63bafa2ab`。
- `generation/combat/attack/W/11-v1.request.json` — `unknown_no_completion_receipt`；SHA `d91688cc618313793841ebb0c197550a4d3c5dd885c035a6ce4bb00baa49bf39`。
- `generation/combat/attack/W/12-v1.request.json` — `unknown_no_completion_receipt`；SHA `0337b1e1c2d8940740fb5b5625fe11ceb128879c907ef119cd6b7fd572ecbe15`。
- `generation/run/E/09-v2.request.json` — `unknown_no_completion_receipt`；SHA `65b205d98eb8e51761d040eb5f6a4a50020cee35ea04f4537da01db2866eda03`。
- `generation/run/N/01-v3.request.json` — `unknown_no_completion_receipt`；SHA `68659a615a528a35f695bc357bb30c97903a2771d499d906e005de1241a05eff`。
- `generation/run/S/16-v3.request.json` — `unknown_no_completion_receipt`；SHA `ee2a2d437af57302e5c52ed9d50438295f90a6839299c5f07018c1621444d24b`。
- `generation/run/SE/13-v6.request.json` — `unknown_no_completion_receipt`；SHA `94d6fd8760779bc67a1d12052c9d438fa230947bffdbf79133df0e9cec318b0f`。
- `generation/run/SE/15-v4.request.json` — `unknown_no_completion_receipt`；SHA `a02f2dcf2658df61ec8fa4e2eda653ec66f06cb4895e18aca7ee9966b143a08d`。

当前索引/源SHA问题 0 项。逐项文件、源PNG、生成记录与回执SHA均在 `review/provenance-completion.json`。
`current-validation.json` 当前绑定 196 张技术快照；新增原图或替换后须重新检查SHA。技术通过不等于动态美术通过。
<!-- CURRENT_SNAPSHOT_END -->

## 本轮修复

八方向128帧按实际脚掌长轴、鞋尖、膝踝及跑向独立复查；用户已撤回月影或垂直方向全部正确的判断，当前没有直接套用的已通过动作模板。高置信度外撇集中在N02/03/10、SE01/02/11–16、NW13–15，共14槽；逐源SHA和采用状态见[脚向复核](review/foot-heading-review-current.json)。14槽修正版已全部合入选表；NW槽15采用14-v8。

此前手脚相位修订也保留：E08接触前脚位、E11平底中撑和右拳过腰；S前三帧承重与头身；SW02/03比例、16→01衔接及整方向固定根高；N04–07与14/15的腿相位和空右臂；NE04、W04/12/16比例；NW换腿、空右臂及腾空次序。N12采用12-v7修正比例并保持左后鞋底/右前鞋跟；失败候选不能按版本号自动采用。

受击、普攻、施法68帧已独立静态复核，保留hit/W03、attack/E10、cast/W02/W05等针对修订。本轮再扫6组战斗脚向，未发现新的明显反向鞋掌或扭踝。见[战斗与S/SW静态记录](review/static-final-ssw-combat.json)及[本轮交接](review/moon-comparison/FOOT_DIRECTION_HANDOFF.md)。

## 正常速度和预览

用户最新要求已落实：离线正常跑步八方向统一每圈1200ms，16帧均为75ms，正好整除；取消E承重权重。单次播放完整16帧，循环首尾不增加停顿。受击40ms、普攻30ms、施法45ms每帧保持不变。参数以[run-timing.json](run-timing.json)和manifest为准。

[动作预览](review/index.html)按清单真实时长播放，可选160/240/512px，默认240px，含正常、¼慢速、暂停和逐帧。[跑步节奏检查](review/timing-grounding/index.html)只保留当前1200ms正常及¼慢放，旧快档和旧加权方案已移出正式预览。改变时长不等于姿态或接地已经验收。

## 验证与边界

[当前验证](review/current-validation.json)绑定当前PNG、来源、选表和清单SHA；[逐帧记录](review/visual-notes.json)区分当前源与旧稿。技术检查包括1024²透明RGBA、1254²独立原生、重复图、索引SHA和动画实际编码时长。

历史浏览器file导航被安全策略阻止；没有使用localhost或其他方式绕过，也没有把编码/静态检查称为实际动态观看。完整循环接地、根点、实际位移滑步和事件仍未经过客户端验证。2026-10-03重新只读核查：D:/work/mmorpg-client现已存在，catalog的v14仍配置30ms/帧并校验480ms/圈，位移动画依赖FramesPerUnit；本素材任务没有修改或运行客户端。证据见review/bamboo-reference/context.json。名义根锚(512,942)是本角色离线候选标定，不是世界地面。

所有生图使用本批内置路径；实际模型/质量未披露，继续为null。当前选中原生母版属于仍需动态验收的在制参考；确认导出与当前引用完整后清理无用拒稿/中间图并保留文字来源，不创建图片备份。只处理本角色目录。

本轮导出后核对196张源/导出SHA，清理generation中188张未采用原生/旧诊断图片（约178.1MiB），无图片备份；保留145张当前选中在制母版及所有文字来源。清理台账见[cleanup-executed.json](review/cleanup-executed.json)。旧审稿/局部selection引用属于历史，不是运行依赖。当前196帧技术及28条正常/慢速动画编码检查全部通过，静态推荐不等于实际动态通过。

## 竹弓少女最新参照与速度更新

用户最新确认竹弓少女当前姿态为参照。同方向完整联系表及疑点原图复查没有确认新增必修手脚硬伤；保留此前修正的道童196张图，来源和像素保持不变。N/NE/W、E/S/SE/SW、NW与东西向战斗分组记录见review/bamboo-reference。此结论仅限静态：N07–09、NE06–07、W07–09过渡及整圈接地仍待实际播放。

最新速度指令独立覆盖此前720ms及分相位方案：所有跑步1200ms/圈=75ms×16，受击40ms、普攻30ms、施法45ms/帧不变。当前动作预览移除旧快档；未改客户端。
