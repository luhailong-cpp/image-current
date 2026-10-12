# 五行奇谈 · 4096 透明人物包

原24个PNG路径和4096×4096画布保持不变。22个职业人物逐张使用内置image_gen重绘，按新版大头、圆脸、短身Q比例统一，保留各人的法器、发型与属性身份。两张参考道童统一复用已确认金发带角色。

每张最终图均为真RGBA。原生生成通常1254×1254；通过generate2dsprite色键清理、脚底对齐后等比导出4096。4096是兼容画布，不代表原生4K细节。

[逐图清单](manifest.json)记录尺寸、Alpha、边界、哈希与生成记录。完整提示词在prompts/，来源ID、原始哈希和技能处理数据在records/。过程母图、裁格和GIF不作为交付；重新生成需运行内置生图并视觉验收，然后用[处理入口](process_portrait.py)导出。

```powershell
python q_daoist_character_pack_4096/build_manifest.py
python q_daoist_character_pack_4096/process_portrait.py --raw <本轮内置生图输出> --id <原文件stem>
```

|角色|最终图片|
|---|---|
|金发带Q道童|[00_reference_topright_boy_transparent_4096](00_reference_topright_boy_transparent_4096.png)|
|冰剑少女|[01_ice_sword_girl_transparent_4096](01_ice_sword_girl_transparent_4096.png)|
|火符少年|[02_fire_talisman_boy_transparent_4096](02_fire_talisman_boy_transparent_4096.png)|
|莲花医者|[03_lotus_healer_girl_transparent_4096](03_lotus_healer_girl_transparent_4096.png)|
|山岳守卫|[04_mountain_guardian_boy_transparent_4096](04_mountain_guardian_boy_transparent_4096.png)|
|天音少女|[05_celestial_musician_girl_transparent_4096](05_celestial_musician_girl_transparent_4096.png)|
|雷法少年|[06_thunder_caster_boy_transparent_4096](06_thunder_caster_boy_transparent_4096.png)|
|月影少女|[07_moon_shadow_assassin_girl_transparent_4096](07_moon_shadow_assassin_girl_transparent_4096.png)|
|炼丹童子|[08_alchemy_prodigy_boy_transparent_4096](08_alchemy_prodigy_boy_transparent_4096.png)|
|竹弓少女|[09_bamboo_archer_girl_transparent_4096](09_bamboo_archer_girl_transparent_4096.png)|
|赤枪少女|[10_crimson_spear_girl_transparent_4096](10_crimson_spear_girl_transparent_4096.png)|
|玉拳少年|[11_jade_fist_flat_top_boy_transparent_4096](11_jade_fist_flat_top_boy_transparent_4096.png)|
|铁刀少年|[12_iron_saber_flat_top_boy_transparent_4096](12_iron_saber_flat_top_boy_transparent_4096.png)|
|风刃少女|[13_short_hair_wind_blade_girl_transparent_4096](13_short_hair_wind_blade_girl_transparent_4096.png)|
|唤雪少女|[14_short_hair_snow_summoner_girl_transparent_4096](14_short_hair_snow_summoner_girl_transparent_4096.png)|
|水龙书生|[15_water_dragon_scholar_boy_transparent_4096](15_water_dragon_scholar_boy_transparent_4096.png)|
|金铃舞者|[16_golden_bell_dancer_girl_transparent_4096](16_golden_bell_dancer_girl_transparent_4096.png)|
|灵篆书生|[17_ghost_script_calligrapher_boy_transparent_4096](17_ghost_script_calligrapher_boy_transparent_4096.png)|
|沙海日轮少女|[18_desert_sun_monk_girl_transparent_4096](18_desert_sun_monk_girl_transparent_4096.png)|
|御兽少年|[19_spirit_beast_tamer_boy_transparent_4096](19_spirit_beast_tamer_boy_transparent_4096.png)|
|星阵少女|[20_star_formation_master_girl_transparent_4096](20_star_formation_master_girl_transparent_4096.png)|
|厨道童子|[21_lidazui_hair_cook_boy_transparent_4096](21_lidazui_hair_cook_boy_transparent_4096.png)|
|执刀小侍|[22_lidazui_hair_waiter_saber_boy_transparent_4096](22_lidazui_hair_waiter_saber_boy_transparent_4096.png)|
|金发带Q道童|[q_daoist_topright_character_full_uncropped_transparent_4096](q_daoist_topright_character_full_uncropped_transparent_4096.png)|

此包是静态人物；移动32帧见[八方向动作](../character_move_8dir/README.md)。未接入客户端、骨骼或战斗技能。
