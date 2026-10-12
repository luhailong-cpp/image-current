# 原创宠物任务接续 — 2026-09-24

## 先读状态

任务未完成。用户最后要求提供接续细节，复制到新窗口继续；本窗口已停止新增生图。
核实时间：2026-09-24，工作区 E:/work/image。

- **有效工作目录：** E:/work/image/designs/pets-original-20260924。
- **有效新母图：0/28。** source/ 与 prompts/ 目前没有新原创文件；下一窗口仍需真正调用内置生图。此前口头分派不代表已产图。
- **已完成准备：** 14项原创名单、用途槽位映射、asset-config.json、manifest模板、3个构建/验证脚本、原创差异审查模板、README。脚本已做语法检查。
- **旧候选：** E:/work/image/designs/pets-20260924。13只 E/W 共26张母图及52张派生图做过技术检查；另有白琉影E候选已生成（归档状态以该目录为准），没有白琉影W。整批因造型太贴近参考游戏已标为“未采用候选”，不能充作新任务完成数。
- 新包 records/technical-validation.json 当前 failed 是因为0张交付，属于真实未完成状态；不是已经产图后发生质量故障。
- 当前没有仍可依赖的子代理、后台作业或持久变量。新窗口重新查看文件决定分工。

## 用户最新有效要求

1. 按 image/designs 已确认风格画14只宠物，用来替换原宠物，供战斗与参战属性UI使用；战斗可能是敌方或我方。
2. 和角色图一样高清；能用 GPT Image 2.5 就用，否则用 GPT Image 2.0。
3. **最新纠正：“元素不要一样，怕侵权，神兽变异元灵都是这样。”** 正式版需原创身份与造型元素，只换画风、颜色、增加玉饰不满足要求。
4. 用户希望持续做完，不要反复询问是否继续。最后要求的是把未完成任务交给新窗口，并非取消绘图。

用户没有逐只确认新名字/物种。README和asset-config内14只新名称与设计是助手为执行原创要求拟定的方案，可以据此继续制作；不要称其为用户逐只批准的定稿。原游戏名只保留为对应用途槽位，不作为新图身份或生成图像输入。

## 新窗口开工顺序

1. 读根 AGENTS.md、designs/README.md、config/image-generation.json、docs/IMAGE_MODEL_POLICY.md、docs/QDAO_ART_DIRECTION.md，以及本目录 README.md、asset-config.json、records/originality-review.json。
2. 查看 designs/team-ui-v2/team-ui-v2.png，实际作为风格图传给生图工具。其他已确认designs样板可补充。新E图仅附项目风格；新W图可附本包同宠的新E图保证身份。外游截图和旧候选不再作为新图造型参考。
3. 按本目录README的14只原创方案逐只生成E和W。可并行分组01/02/04/05/06、07/08/09/10/11、03/12/13/14；必须真实生图与落盘，不把分派任务当进度。
4. 每次生成前保存真实提示词到 prompts/<slug>-E.txt 或 -W.txt。生成后复制工具原始PNG到 source/<slug>-E.png 或 -W.png，保留原始工具文件，在 records/<slug>-E.receipt.json 等保存实际调用与结果来源。
5. 逐张检查轮廓、服装、法器、配色安排是否体现新身份；与原参考存在明显元素差异才接受。看清E/W完整肢体、道具、尾翼、耳角以及真正朝向。失败图保留自己的记录，另版重试。
6. 原生图到后在asset-config逐宠设置实际头像crop；坐标来自新E母图，不复用旧候选crop。构建、查看总览、验证全部56张正式静态输出。
7. 交付清楚标明素材包状态、真实原生分辨率、实际模型证据、静态用途与未完成的客户端接入。

14项具体名字、slug与简明原创形态在 [README](README.md) 和 [asset-config](asset-config.json)。优先落地其中的差异，而不是沿用旧图脸型/发型/服装/伴生物重新上色。

## 风格与规格

- 美术：明亮干净、圆润饱满的道家Q版高清手绘，人物约2.2–2.8头身，大头短身短肢；精细毛发/丝绸/陶玉但克制反光，保留中间调；点缀少量结绳、花灯或桂花元素。
- 每只独立生成，不用合图小格放大。原生短边至少1024；旧批实际为1254×1254，不是原生4K。
- E：敌方在左上，斜前朝右下。W：我方在右下，真正斜后朝左上，看到背部；分别绘制，不能把前面水平翻转冒充背面。
- 单只完整全身，中央约75–80%留安全边距。背景隔离，无UI/文字/地台/地面光圈；保持全耳角、尾翼、法器、脚手。
- source保留原生；runtime每宠idle_E.png/idle_W.png为1024×1024真RGBA，共同缩小因子、pivot(0.5,0.08)（左下原点）。
- UI每宠fullbody_1024.png和portrait_512.png，头像人工取景。来源不足目标尺寸时保持真实原生并留白，不能上采样冒充细节。
- 这是静态双方向包，不包含待机/攻击/行走等动画。旧角色V14的停止/审批历史不构成此次已授权宠物生图的阻塞。

## 内置工具和当前环境经验

默认使用内置 image_gen.imagegen，使用 generate2dsprite 与 gpt-image 技能。用户没有授权付费API/CLI备用路线。
2026-09-24已核实官方2.5开放，config仍是gpt-image-2.5-sunburst / max / ChatGPT Images 2.5；verify_on已更新2026-09-24。新任务继续按项目政策核对。
官方依据：
- https://openai.com/index/introducing-chatgpt-images-2-5/
- https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst

本次内置接口只开放prompt、referenced_image_paths、num_last_images_to_include，没有model/quality选择器。不能把配置目标当实际锁定参数。旧批PNG C2PA仅给出ChatGPT / gpt-image，不能确认2.5或2.0分支；actualModel/actualQuality仍null。缺乏选择器也不等于已证明只可用旧模型。

此窗口的Windows默认沙箱出现 helper_unknown_error: setup refresh had errors：
- exec_command默认无法启动；require_escalated可正常读写本任务工作区，这是环境启动故障，不是人工或自动审核拒绝。
- view_image和image_gen referenced_image_paths同样读取失败。
- 可用替代：以PowerShell System.Drawing只读加载原图，在内存生成约1100宽JPEG缩略图，输出base64给functions image("data:image/jpeg;base64," + result.output.trim())，不把大段base64作为text输出。查看后用这些没有落盘路径的对话图像作参考：E num_last_images_to_include=1；W先显示style再显示新E，num_last_images_to_include=2。不要同时提供两种引用参数。
- 这是输入通道替代，不是API调用。原始完整参考文件路径和实际缩略通道应保存在receipt。
- 新窗口先尝试常规工具；只有同类故障仍存在才沿用此办法，不修改系统/权限配置。
- tools结果有image_url及output_hint；用generatedImage(result)显示，output_hint包含本次真实原文件路径。复制该文件到workspace，原始文件保留。
- 旧批提示pure #FF00FF背景，但工具实际返回真RGBA。以真实PNG为准，保留alpha；若确实有洋红底才运行抠色。不要改掉宠物本身的粉红。

每张图记录配置快照、实际提交model/quality(null)、真实返回值、prompt、参考用途、尺寸、SHA256、准确时间和输出路径。图旁generation.json与派生derived.json由build_pack写入；底层凭据receipt需要调用者真实保存。模型证据提取复用 qdao_original_roster_v14_hd/tools/inspect_image_provenance.py，无需改旧角色工具。

## 构建与验收

在 E:/work/image 执行：

```powershell
python designs/pets-original-20260924/build_pack.py
python designs/pets-original-20260924/build_overviews.py
python designs/pets-original-20260924/validate_pack.py --require-complete
```

增量可加 --only <slug> 给build_pack。两个方向齐才统一尺度导出；每宠应有2张runtime+2张UI，共56张。来源28张，各自有来源链。极小孤立噪点和远离主体的alpha=1底噪可确定性清理，保留原生源和修改记录。
previews/E-roster.png和EW-roster.png只排版已生成的图作视觉检查，不能替代实际单图。
完成标准：14/14双向，28真实原生源、56正式透明导出，独立头像取景，全部技术校验通过，逐宠原创差异和E/W视觉核对有据，用户可查看总览。技术报告不冒充用户确认或Unity验收。

## 客户端边界与已知接线信息

尚未写入 E:/work/mmorpg-client。此前异步询问“先交素材/直接接入新增14只”，用户没有回答，已授权的绘图继续完成。
现有客户端无法把14参考名直接等同现有ID：
- Assets/Scripts/UI/Ugui/Pet/PetPanel.cs:518 仅ModelId1001→portrait_lingyue、1004→portrait_yunjiujiu，其余占位。
- Assets/Scripts/UI/Ugui/Battle/BattleArtCatalog.cs:166 确认敌E/我W与feet pivot(0.5,0.08)。
- Assets/Scripts/UI/Ugui/Battle/BattleStage.cs:41 宠物显示比例约主人×0.65。
- Assets/Scripts/UI/Ugui/Battle/BattleUnitView.cs:990 目前外观分支只有Monster/非Monster，Pet会落入人物外观，需要后续真正宠物入口适配。
这些位置来自只读盘点，接入时复核当前代码。原参考名是slotReferenceName，clientModelId为null；不能自称旧14只已被替换或已通过引擎测试。

## 旧稿与其他任务

旧候选保留在 designs/pets-20260924，README已经标记停用。它们的图片不用于新包生成或正式交付。旧工具报告仅描述旧稿技术状态。
designs/city-npcs-20260924是本任务开始时就有的无关未跟踪目录，保持不动。没有为本任务提交git或push。

