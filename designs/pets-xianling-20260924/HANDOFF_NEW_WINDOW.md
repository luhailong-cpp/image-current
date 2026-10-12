# 14只原创宠物·仙气提升版 — 新窗口交接

交接日期：2026-09-25（按当前会话日期）。原始生成与审计时间以各receipt/元数据为准，不改写。
工作区：`E:/work/image`。本轮当前目录：`E:/work/image/designs/pets-xianling-20260924`。

## 用户当前目标与优先级

用户明确选择“本次截图对应的14只都重新提升仙气”，随后再次强调“要求美观”。延续已确认的高清手绘道家Q版完成度，脸部自然精致、配色协调、服装轻盈、玉金与毛羽细节清楚。最新仙女参考只取美感和材质，不复制蓝发、粉羽舟、服装或姿态。神兽、变异、元灵同样必须原创，不能只换画风/颜色。

每只交付：E敌方斜前朝右下；W我方真正斜后朝左上（独立绘制、有后脑/背部/鞋跟或后肢，不可镜像）；参战属性UI透明全身和头像。

用户最后要求本窗口生成交接后到新窗口做。当前不要再开新窗口内以外的后台生图；直接从下面的真实进度继续，不要再询问是否覆盖14只。

## 目录关系，切勿混淆

- `designs/pets-20260924`：旧未采用候选。
- `designs/pets-original-20260924`：上一轮原创包，已完成28/56；其早期“0/28、0/56”已过时。
- **`designs/pets-xianling-20260924`：本次14只全部新绘的仙气提升版，后续工作以这里为准。** 不用旧包图片替换新图。
- 新包完整源图/导出已实际存在，当前是美观收尾和记录整理阶段，不是0张，不应无依据重画全套。

## 已完成的事实

- 14只、28张正式原生PNG均为1254×1254；E/W分别实际生成。
- 56张RGBA交付已导出：28战斗图、14全身、14头像。
- 三张总览齐：`previews/E-roster.png`、`previews/EW-roster.png`、`previews/portrait-roster.png`。
- `records/technical-validation.json` 本窗口已运行 `validate_pack.py --require-complete`，结果passed：28来源、56输出、3总览，pending/errors均空。**这只是技术验收，不等于最终美观验收。**
- `records/provenance-audit.json`：28正式+1本轮候选共29张与内置工具原件、output_hint及SHA吻合；对旧两包229个PNG查重，0字节复用；实际prompt/receipt/生成记录齐。
- `records/requested-roster-mapping.json`：17张原游戏截图去重14只，白琉影4张只算1只。
- 每只原生图已由生成执行者检查方向与主要轮廓；root尚未完成三张最终导出总览的完整美观复查。
- `source/native-archive`保留与原图字节相同的归档，`.generation.json`和`.derived.json`来源链已建立。
- 未接入客户端、无动画；所有`clientModelId`仍null。无需本轮自行接入Unity。

## 本轮准确14只

|截图槽位|原创名|文件slug|
|---|---|---|
|火鸦|烛翎|01-zhuling|
|粉衣仙子|绛铃|02-jiangling|
|雪狐|霜团貂|03-shuangtuan|
|秋棠仙子|桂灯童|04-guideng|
|羽鹤仙卿|砚羽灵|05-yanyuling|
|翎凤真君|岚铎仙|15-landuoxian|
|精卫|汐螺|06-xiluo|
|应龙|苍嶂麟|07-cangzhanglin|
|青鸾|竹风狸|08-zhufengli|
|景云|赤砂魁|09-chishakui|
|墨渊|玄潮龟|10-xuanchaogui|
|玉霄|月弦师|12-yuexianshi|
|幽雪|露华灵|16-luhualing|
|白琉影|绯耳灵|14-feierling|

上轮多出的赤天/九华不是这次截图14只，勿纳入。原创名字/身份是为满足原创要求提出的设计，不代表用户已逐只批准命名。当前方向和实际设计见`asset-config.json`。

## 下一步必须处理

1. **先实际打开三张总览及必要的1024单图**，以用户反复强调的“美观、有仙气”为主审：面部表情、配色、轻盈程度、过密装饰、轮廓完整、E/W身份与道具一致、头像是否裁掉耳饰/髻冠。必要时只重绘有问题的一只或一向；用其新E作身份参考。不能仅凭文件存在宣布美观通过。
2. 处理`processing-report.json`的3项警告：03-shuangtuan W有13个小连通像素待判断（可能细毛/胡须，勿为消警告误删）；08-zhufengli E和10-xuanchaogui W有可见洋红/粉像素待判断。这两张是RGB洋红底，需要实看提取后的封闭背景洞/边缘污染。
3. 如果`records/*cleanup*proposal*`或相关边缘提案在交接末尾已落盘，先读；只将实看通过、SHA绑定的小范围清理加入config。`build_pack.py`已有`reviewedMagentaPocketCleanup`和`magentaEdgeDecontamination`（radius1..3）支持，避免全局去粉/紫/蓝。原生source不修改。
4. 规范部分视觉JSON字段，然后重建manifest：03/12/14/16当时使用`assistant-visual-pass`，08/09/10使用`assistant-visual-reviewed`，处理器当前不识别。已通知执行者补齐但以磁盘最新状态为准。`visual_review_state`接受`passed-agent-visual-review`等；需要实际`findings.E`、`findings.W`和`findings.originality`或等效`directions`/`originality`。只整理真实检查证据，不机械改状态冒充验收。
5. 当前`records/originality-review.json`是首次汇总，08/09/10可能actualImageAudit为null；补真实原创差异。manifest的`originalityReview=partial`与上述schema不统一有关，不能只改成passed掩盖。
6. 所有图修正/裁区/清理配置落盘后，重新build、三张总览、validate。最终写`records/final-visual-review.json`、完善README，并交付总览和路径。将用户逐只认可、助手视觉审查、技术验收、客户端接入区分记录。

## 透明边缘与候选的已知事实

- `records/source-edge-audit.json`已覆盖正式28张；强alpha(>=16、>=128)主体均不触原生画布边。低alpha彩色点在工具直接展示中很明显，在正常合成时很淡；不据此全局删除合法颜色。
- 烛翎E真实主体bbox(alpha>=16)为[10,14,1250,1194]，右边仅4px，但翼尖完整。输出共同缩小已留安全边，不需仅因贴边重生。
- 绯耳灵E首稿耳尖触边，已保留`source/candidates/14-feierling-E-candidate01.png`及独立prompt/receipt/generation记录；正式E重新生成且完整。正式E额外引用这个**本轮原创候选**作视野修复，不是旧包/游戏造型。
- 14绯耳灵E/W共13个高alpha极红像素经实看是腰间红结/流苏，保留。
- 原生边缘审计与导出后洋红洞检查不是一回事，08E/10W仍按processing-report实查。

## 文件与导出契约

- `source/<slug>-E.png`、`-W.png`：1254×1254原生，旁附`.generation.json`。
- `runtime/<slug>/idle_E.png`、`idle_W.png`：1024×1024 RGBA；每宠E/W共用缩小比例；左下原点pivot[0.5,0.08]，顶部原点脚点[512,942]；不放大母图、不镜像。
- `ui/<slug>/fullbody_1024.png`：透明全身（取E）。`portrait_512.png`：人工观察新E后取景的512透明头像，不放大原生细节。
- `asset-config.json`已合并14份新的crop/anchor提案；`records/<slug>-config-proposal.json`保留提案。
- `records/prepare_export.py`是本窗口首次合并脚本，**后续不要盲目重跑**：会重新应用旧提案/写root4只review，覆盖后来手调。后续直接编辑asset-config及相关审查记录。
- `manifest.json`、`processing-report.json`由build更新；总览有派生哈希；每次改输出后重新出总览。

## 建议阅读顺序

本文件 → 当前README/asset-config → 三张previews → processing-report → technical-validation → 各宠visual-review和originality-review → provenance-audit/requested-roster-mapping。

仍遵守根AGENTS.md、designs/README.md、config/image-generation.json、docs/IMAGE_MODEL_POLICY.md及所需美术交接。图像任务已使用imagegen、generate2dsprite、gpt-image技能；后处理仅抠底、裁切、缩放、对齐、组合预览，不用脚本画新宠物。

## 生成入口、模型和真实来源

优先内置`image_gen.imagegen`；用户选择2.5可用则2.5，否则2.0，不授权额外计费API。当前项目配置目标`gpt-image-2.5-sunburst` / `max`，产品目标ChatGPT Images2.5。此前已核对官方页面：

- https://openai.com/index/introducing-chatgpt-images-2-5/
- https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst

但本次内置工具没有model/quality入参且没有可靠返回实际版本，所有图actualModel/actualQuality为null并有未确认原因。配置目标、提示词要求和公告均不是实际锁定版本证据，不补写成2.5/max。原生不是4K，不把放大称为原生高清。

真正使用的风格参考：`references/approved-team-ui.png`（原路径designs/team-ui-v2/team-ui-v2.png）及`references/ethereal-finish.jpg`（用户最新仙女截图，来源清楚保留于input-index）。原17张游戏截图仅作槽位/差异分析，没有作生成造型参考。W再附该宠新E；14正式E视野修复还附本轮candidate01。

每次生成前保存真实prompt；完成后复制工具PNG，保留工具原件，保存receipt中source/output_hint/起止时间/sha/实际输入refs与channel/configSnapshot/submittedParameters/实际返回未知项。不可倒填臆测prompt。

参考路径验证规则会拒绝path含codex-clipboard或pets-20260924；本轮用户授权的最新仙气图片已经按字节归档到references/ethereal-finish.jpg。早期实际从TEMP读取的receipt保留readFrom及archiveByteIdentical，不能隐藏原始来源。

## 本机工具输入故障恢复经验

此前默认exec/view_image/node_repl报Windows sandbox初始化`helper_unknown_error: setup refresh had errors`。`exec_command`使用require_escalated可正常完成已授权工作区读写，自动审核未要求用户重复确认。新窗口先试正常通道，是否仍有故障以实测为准。

本窗口读取本地参考时用PowerShell System.Drawing在内存等比缩放至JPEG，Base64通过functions.exec的image()显示；没有改参考文件。随即生图使用`num_last_images_to_include`，E通常2(项目风格+仙气参考)，W通常3(前两张+新E)。工具图片输入机制不能混用，必须核对最后N张真是目标参考。不要把输入故障当成需要API密钥。

查看PNG时可用同样的只读内存中性底合成，避免直接黑底预览低alpha色点误判。若工具恢复，优先正常view_image/referenced_image_paths。不要在外部付费API重试。

## 重建和验收命令

在`E:/work/image`执行：

```powershell
python designs/pets-xianling-20260924/build_pack.py
python designs/pets-xianling-20260924/build_overviews.py
python designs/pets-xianling-20260924/build_portrait_overview.py
python designs/pets-xianling-20260924/validate_pack.py --require-complete
```

只改某宠时可`build_pack.py --only 08-zhufengli`等，但之后仍重出全部总览与validate。技术通过目标28/56/3，pending/errors为空。最终人工看浅/深底合成、背面结构、头像完整性并记录；不得拿脚本passed代替美观判断。

## 新窗口的第一步

先查看三张总览，读3项待查警告及最新边缘提案，整理视觉记录格式。用户想要美观而有仙气的实际成图；在已有28张上完成有依据的修正和最终交付。不要回到仅写方案，不要把本交接当作已全部美观验收通过。
