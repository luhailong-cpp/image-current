# 00 金发带道童 · 动作素材交接

> 当前交付：60ms/帧，16帧共960ms；相邻位置两帧共120ms，¼慢放3840ms/圈。196张图片内容和68帧战斗时序保持不变。此前75ms/1200ms记录为历史；当前以 run-timing.json、manifest 与预览为准。
> 2026-10-05全动作复核：196帧完成静态检查，本轮补修W03/W11与NE04/NE12摆臂经过位、SW06悬空腿经过位。五张已合入正式导出；跑步16×75ms=1200ms。相邻落脚位置各两帧依次推进。动态及客户端仍未验收。详见[本轮完整记录](review/full-body-20261004/summary.json)。

> 2026-10-04最新：八方向跑步128帧接地与手脚修订已合入196张导出；落脚位置依次推进，各相邻位置两张独立姿态，正常16×60ms=960ms。逐图及独立静态复核完成；实际动态与客户端未验收。当前交付见[DELIVERY.md](DELIVERY.md)。

当前196槽资源已收齐，八方向128帧的新接地选表已合入。运行资源以manifest.json中的frames[].file为准；selected-new.json是本角色新增/替换原生选帧的唯一导出入口，局部selection是交接记录，不能按最高版本自动选图。静态修复、技术检查与整段动态/客户端通过分别统计。

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

## 数量与节奏

- run八方向各16，共128；离线正常1200ms/圈，统一75ms/帧。
- hit E/W各6，共12；40ms/帧，240ms/段。
- attack E/W各12，共24；30ms/帧，360ms/段。
- cast E/W各16，共32；45ms/帧，720ms/段。

八方向跑步均匀75ms×16=1200ms；取消E权重，正式预览不再提供旧快档。已写入run-timing.json、manifest逐帧字段和导出记录，以及预览源码及生成脚本；慢放为¼。战斗未随跑步减速，客户端运动/伤害/技能配置未修改。

## 修复与审查

本轮脚掌外撇修复范围N02/03/10、SE01/02/11–16、NW13–15。依据实际鞋尖和膝踝连接，未用缩窄腿间距代替摆正脚掌。完整源SHA与采用情况见review/foot-heading-review-current.json。先前跑步摆臂、支撑腿和比例修订以及战斗4个针对修改均保留，见review/visual-notes.json和STATUS.md。

输出1024×1024 RGBA来自独立原生1254×1254全画布；每方向只用export-settings.json一套固定缩放/偏移，没有镜像、插值、复制凑帧、逐帧bbox拟合或最低像素贴地。SW固定根高单独校正，名义根锚(512,942)仍是离线候选；斜向近远脚透视不强制贴同一屏幕水平线。

## 检查与接入边界

review/index.html默认240px并按manifest真实逐帧时长播放，支持160/512px和正常/¼慢速/逐帧。review/animations保存14组完整联系表及正常/慢速WebP。review/timing-grounding只呈现当前1200ms正常/慢放检查；review/bamboo-reference为同方向只读对照，本页参考跑步也按75ms显示，保留其源manifest时长证据。

历史file浏览器导航被安全策略拒绝，未绕过。静态看图、WebP时长和JS边界检查不等于浏览器实际动态验收；完整接地与首尾观感仍须实播。2026-10-03重新只读确认D:/work/mmorpg-client现已存在，旧“不存在”记录已过时；catalog v14当前30ms/帧、480ms校验及FramesPerUnit位移关系仍需集成任务联动更新，不能只拷贝PNG就认为1200ms已在游戏生效。本任务未修改或运行客户端；证据及代码SHA见review/bamboo-reference/context.json。

## 来源与刷新

内置image_gen；配置目标gpt-image-2.5-sunburst/max，实际提交/返回型号质量未披露的字段为null。原始失败与无完成证据请求区分记录，文字来源和SHA不因清理旧图而改写。共享旧combat/run批次只读；不改其他角色或Git。

更新次序：选表 → tools/export_selected.py → tools/review_frames.py all --sources sources.json → tools/render_previews.py与tools/render_timing_previews.py → tools/verify_preview_timing.py → tools/refresh_validation.py → tools/audit_provenance.py。导出前检查动作路径和原生SHA唯一性，避免跨动作串图。当前选中母版作为动态未验收在制参考保留；拒稿/中间图在导出及引用闭合后按清理台账删除，来源文字保留。

本轮导出后核对196张源/导出SHA，清理generation中188张未采用原生/旧诊断图片（约178.1MiB），无图片备份；保留145张当前选中在制母版及所有文字来源。清理台账见[cleanup-executed.json](review/cleanup-executed.json)。旧审稿/局部selection引用属于历史，不是运行依赖。当前196帧技术及28条正常/慢速动画编码检查全部通过，静态推荐不等于实际动态通过。

## 竹弓少女最新参照与速度更新

用户最新确认竹弓少女当前姿态为参照。同方向完整联系表及疑点原图复查没有确认新增必修手脚硬伤；保留此前修正的道童196张图，来源和像素保持不变。N/NE/W、E/S/SE/SW、NW与东西向战斗分组记录见review/bamboo-reference。此结论仅限静态：N07–09、NE06–07、W07–09过渡及整圈接地仍待实际播放。

最新速度指令独立覆盖此前720ms及分相位方案：所有跑步1200ms/圈=75ms×16，受击40ms、普攻30ms、施法45ms/帧不变。当前动作预览移除旧快档；未改客户端。
