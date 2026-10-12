# 15 水龙书生 · 当前修复版合并交接

更新时间：2026-10-05T10:01:33.577877+00:00

196张正式PNG已导出，14组完整连图已实际静态逐帧复核。最新版本没有通过完整动态播放观感验收：浏览器工具读取本地file页面被URL安全策略拒绝，未绕过限制。不要把静态通过、文件齐全或旧audit/final-review.json当成当前动态通过。客户端未接入、未运行测试，用户尚未验收。

## 文件和来源

- 当前图像权威：manifest.json（每张相对路径、SHA、源SHA、时长、事件）；provenance/derived/*.json保留完整原始来源链。
- 当前静态审核：audit/current-static-review.json，绑定196槽成品及来源SHA。旧final-review.json保留为已撤回历史。
- 交付检查：audit/final-delivery-check.json/md；技术核验不能替代动态观感验收。
- 当前完整预览：preview/all-directions.html；单组正常、0.25倍慢速、暂停和逐帧：preview/index.html。
- 动图：preview/run-all-directions.gif和各组uniform960/normal、slow GIF；全部从当前runtime导出。
- 逐图提示词、真实参考、请求、回执及模型证据在prompts与provenance；旧来源和被替换图的SHA保留。

当前选择为195张本机生成/局部编辑、1张本地已提交旧图复用。相比已撤回旧final-review的来源映射，113个槽位已替换；其中战斗动作1个。没有获取另一台电脑未提交图片。

## 本轮实际修复

以用户指定09竹弓少女同方向实图为动作观感参考，保留水龙书生身份、画法、右手扇、左手空闲及左胯玉佩。错误外撇、重复同足支撑、近远腿遮挡、接地位置及部分扇手跳变均针对性修正；正确旧帧保留。

最新视频反馈轮针对性替换21个独立槽位，包含跑步脚向17帧、跑步摆臂过渡4帧、战斗手臂1帧；N11脚向和摆臂两类重叠。其他175帧保留原成品SHA。具体槽位：run-N-01、run-N-02、run-N-07、run-N-08、run-N-09、run-N-10、run-N-11、run-N-15、run-NE-08、run-NE-09、run-NE-12、run-NE-13、run-NE-15、run-E-03、run-SE-04、run-SE-05、run-SW-10、run-W-03、run-NW-03、run-NW-10、attack-W-03。修前/修后逐图SHA见audit/video-direction-20261004/repair-result.json。视频实际解码并查看四段连续抽样；其中角色小且遮挡，仅用作动作轴线参考。新图原生逐张与新版连图已静态复核；脚向修正不靠移动整图或最低像素贴地。

最新接地解释是同一足在沿行进轴的连续相对位置各两帧，然后换足。N/S/NW/SW第一足为15/16→01/02→03/04→05/06，第二足为07/08→09/10→11/12→13/14；NE/E/SE/W为16/01→02/03→04/05→06/07，另一足08/09→10/11→12/13→14/15。每位置两张真实独立姿态，120ms，不是复制同图，也不是左右外八。

NW07–10按实际支撑足位置重排独立原画；E12/13同理，逐槽旧来源不改名冒充新图。NW11加入扇手经过远侧的遮挡过渡，SW05/06增加同一支撑脚后推；W06/16局部调整接触高度。E11、SE11及W03/04/11摆臂衔接已修。

剩余观感核验：正常1倍与0.25倍整圈、首尾16→01、NW07–12和SW03–07衔接。SE08–10裤裆被衣摆遮挡，足别确认信心中等；部分接地点仍有约10–25原生像素变化，不宣称逐像素锁地。

## 帧组

| 动作 | 方向 | 帧数 | 当前检查 |
|---|---|---:|---|
| run | N | 16 | 静态已审；最新动态待验收 |
| run | NE | 16 | 静态已审；最新动态待验收 |
| run | E | 16 | 静态已审；最新动态待验收 |
| run | SE | 16 | 静态已审；最新动态待验收 |
| run | S | 16 | 静态已审；最新动态待验收 |
| run | SW | 16 | 静态已审；最新动态待验收 |
| run | W | 16 | 静态已审；最新动态待验收 |
| run | NW | 16 | 静态已审；最新动态待验收 |
| hit | E | 6 | 静态已审；最新动态待验收 |
| hit | W | 6 | 静态已审；最新动态待验收 |
| attack | E | 12 | 静态已审；最新动态待验收 |
| attack | W | 12 | 静态已审；最新动态待验收 |
| cast | E | 16 | 静态已审；最新动态待验收 |
| cast | W | 16 | 静态已审；最新动态待验收 |

跑步16×60ms=960ms/圈，HTML仅保留该正常档与慢放；GIF直接以60ms逐帧编码，共960ms。受击6×40=240ms，普攻12×30=360ms，施法16×45=720ms，未跟随跑步改速。各GIF实际编码时长详见preview/*.json。

60ms以用户在本角色聊天最新纠正“不是已经改成60ms 一帧了吗”为准，覆盖批次README中75ms旧要求。变更证据与旧时序快照见audit/run-timing-change-60ms-20261005.json；未修改共享文件。

跑步事件已按同一支撑足沿行进轴连续相对位置各两张独立姿态更新，每位置120ms，见audit/current-support-sequence.json。旧腾空/离地事件保存为legacyEvent，不能沿用作当前接入事件。战斗动作事件以manifest逐帧event为准，当前非空标记为：[["hit-E-03", "maximum_recoil"], ["hit-W-03", "maximum_recoil"], ["attack-E-03", "windup_peak"], ["attack-E-05", "contact"], ["attack-E-06", "strike_peak"], ["attack-E-12", "recovery_end"], ["attack-W-03", "windup_peak"], ["attack-W-05", "contact"], ["attack-W-06", "strike_peak"], ["attack-W-12", "recovery_end"], ["cast-E-09", "cast_release_begin"], ["cast-E-10", "cast_release_peak"], ["cast-W-09", "cast_release_begin"], ["cast-W-10", "cast_release_peak"]]。这些是素材接入标记，未在客户端测定。

## 画布与模型

正式PNG为1024×1024 RGBA；统一完整原生1254→940，置于(42,49)，全局根(512,942)。不按单帧最低脚/包围盒调整，不镜像、复制、扭曲或插值凑帧。

内置image_gen宿主管理入口，配置目标GPT Image 2.5 Sunburst / max。工具没有型号/质量选择器，实际返回未披露，actualModel/actualQuality为null；目标不冒充实测。未使用收费API/CLI。

## 合并与图片保留

只合并本角色目录，按manifest的路径和SHA核对，另一台电脑的未提交内容由用户合并。本聊天未切分支、未暂存、未提交、未推送或写其他角色。

最终runtime及44张必要预览保留。已淘汰图片在技术核验后清理，保留逐图来源文字和删除SHA；历史514张清理记录不覆盖。当前入选原生图仍作为待动态复核的当前设计输入按需保留，不复制图片备份。清理记录以audit/retention-executed.json及后续批次记录为准。

本轮已清理39张淘汰图和中间图，逐图删除SHA见audit/retention-executed-video-axis-20261005.json；清理前技术核验196/196通过，0错误。

技术核验并写报告：python tools/final_delivery_check.py --write-report。重建预览用render_sequence_previews.py、render_run_overview.py、update_progress.py；不要从已清理的旧source全量重建。finalize_review.py只在新的真实动态审核记录完成并完全匹配当前SHA后才能使用。
