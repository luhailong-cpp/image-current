> **最新接续入口已更新：** 用户追加“本次截图对应14只全部提升仙气、要求美观”，新绘批次位于 [pets-xianling-20260924](../pets-xianling-20260924/HANDOFF_NEW_WINDOW.md)。新批次已28/28母图、56/56导出，技术通过，最后美观与边缘收尾详见新交接。以下保留的是上一轮原创包记录，不是当前仙气提升版状态。
# 原创宠物任务接续 — 当前交付

更新：2026-09-24T11:57:11.860755+00:00。工作区 `E:/work/image/designs/pets-original-20260924`。

## 先核对当前文件

14只新原创宠物均已完成独立 E/W 母图及四项正式静态导出：28张原生源图、56张透明交付。旧“0/28、0/56”是10:32 UTC的准备阶段快照，已移入 [历史接续说明](records/handoff-initial-0-of-28.md)。实际图像生成时间晚于该快照。

1. 当前交付入口：[README](README.md)、[manifest](manifest.json)。查看 [E总览](previews/E-roster.png)、[E/W总览](previews/EW-roster.png)、[头像总览](previews/portrait-roster.png)。
2. 完整性以 [技术验收](records/technical-validation.json) 为准，应为 `passed`，`checkedSourceCount=28`、`checkedOutputCount=56`、`pending=[]`、`errors=[]`。
3. 视觉与来源另读 [最终视觉复查](records/final-visual-review.json)、[逐宠原创差异](records/originality-review.json)、[工具来源审计](records/provenance-audit-20260924.json)。文件存在、技术通过、助手视觉通过与用户逐只确认是不同事实。

## 使用契约

- `source/<slug>-E.png` 和 `-W.png`：原生1254×1254，独立生成；原图保留不变，旁附`.generation.json`。
- `runtime/<slug>/idle_E.png`：敌方斜前朝右下。`idle_W.png`：我方真正斜后朝左上，有背部结构。1024×1024 RGBA，每宠两向共同缩小因子，脚点`(0.5,0.08)`（左下原点）。
- `ui/<slug>/fullbody_1024.png`：透明全身。`portrait_512.png`：实际新E源图人工取景头像。导出不放大原生细节，旁附`.derived.json`。
- 当前仅静态图，尚未接入客户端、没有宠物动画，`clientModelId`仍为`null`。
- `designs/pets-20260924`仍是未采用候选；本包不引用它或外游截图作为造型输入。名字及方案是为执行原创要求拟定的身份，非用户逐只批准的名字。

## 来源、模型与透明处理

28张源图的receipt、原始内置工具输出、哈希与原生归档均匹配；28份实际prompt齐全。E只附已确认项目风格，W额外附同宠新E。模型配置目标为2.5/max；内置接口未开放型号或质量选择器，C2PA仅给出ChatGPT/gpt-image，实际2.5或2.0及质量均未确认。保持逐图null和理由，不回填为配置值。

玄潮龟E是本批唯一RGB洋红底来源，导出采用边界抠底和已记录的边缘去污染；绳结下封闭间隙另以源图哈希及小范围配置清除69个alpha像素，原生坐标实际范围`[195,523,204,536]`。原始RGB与PNG不变；证据见其视觉复查和派生记录。

## 若后续需要重建

在仓库根目录运行：

```powershell
python designs/pets-original-20260924/build_pack.py
python designs/pets-original-20260924/build_overviews.py
python designs/pets-original-20260924/build_portrait_overview.py
python designs/pets-original-20260924/validate_pack.py --require-complete
```

修改原图或crop后重建对应宠物及总览，再检查透明边缘、方向、头像与来源哈希。重生图仍遵守根AGENTS、designs风格索引和统一模型策略。

本机默认exec/view_image仍遇到`helper_unknown_error: setup refresh had errors`。已授权工作区操作可用require_escalated运行；只读System.Drawing在内存输出JPEG供对话查看。若需再次生成，先尝试正常输入通道；同样故障时用可见对话参考图和`num_last_images_to_include`，并如实记录。详见历史接续说明的工具恢复段。

客户端接入是后续工作：按用户新的接入指令复核实际工程与宠物ID映射；当前素材技术或视觉通过不代表Unity验收。旧接线盘点仅供线索，见历史接续说明末段。

