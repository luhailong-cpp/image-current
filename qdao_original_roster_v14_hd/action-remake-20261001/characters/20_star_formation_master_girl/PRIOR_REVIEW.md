# 星阵少女旧成果复核
核对日期：2026-10-02（America/New_York）。范围仅本角色本机文件；旧目录只读。
- run-correction-20260930/characters/20_star_formation_master_girl 实际只有 HANDOFF.md，没有 PNG。
- combat-20260929/characters/20_star_formation_master_girl 无本角色成图目录；handoffs-20260930/20_star_formation_master_girl.md 的 0/68 与当前实图相符。
- recovery-20260921/20-final 保留旧 walk 128 张、idle 8 张。历史 acceptance.json 的 passed 属于旧步行交付；不能覆盖用户后来的跑步修正要求。
- 实际查看画像、E/W idle、walk/E/01、05、09、13，及 designs/jubaozhai-ui/02-characters.png。E01/E09 双臂都将盘卡持于胸前，近侧肩肘未随反相腿作明显反向摆动；E05/E13 同样固定持物，脚步主要交替开合。不能直接把这四张计为新的跑步循环。
- 旧导出采用逐帧 lowest-alpha/feet y=942；这会消除跑步的腾空高度。本批使用全画布统一缩放、固定根点，保留运动起伏。
- 旧图继续作为角色身份、服装、朝向与握持参考；未改写旧模型来源、未覆盖旧资产。未审的其他旧帧仍保留原用途，不宣称逐帧拒绝全部128张。
- 已沿用以前的方法：单帧内置生成，实际传入角色与风格参考，逐图来源，固定画布导出，正常/慢速/逐帧预览。没有复制、镜像、扭曲或插值凑数。

新图配置目标沿本批为 GPT Image 2.5 Sunburst / max。2026-10-01实际打开官方模型页确认支持max：
https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst
这只是产品和配置证据；本次内置工具没有型号和质量选择器，实际参数与实际返回型号/质量均未确认。

