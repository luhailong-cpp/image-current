# 主城与场景重绘 · 完成交付

> 2026-09-12 新增：[蓬莱岛、东海渔村、揽仙镇完整大地图](qdao_large_city_maps_20260912/README.md)。已按最新要求取消统一青绿金配色，另整理[此前5个大地图版本](qdao_large_city_maps_20260912/catalog/已有大地图索引.md)。

2026-09-10批次已完成高清主城地图与用户确认的五类场景美术，统一为Q版道家、玉绿暖金象牙米白，配合春节、元宵、中秋的适量节庆点缀。所有正式文件保存在本image资源目录。

## 高清主城地图

- [6144×6144总图](tianyong_festival_hd_20260910/tianyong_city_master_6144.png)
- [2048总览](tianyong_festival_hd_20260910/tianyong_city_master_preview_2048.png)
- [36张1024×1024切片](tianyong_festival_hd_20260910/Tiles/)
- [主殿原尺寸细节](tianyong_festival_hd_20260910/qa/main_hall_100percent.png)
- [主殿前后对照：左为小稿放大，右为分区重绘](tianyong_festival_hd_20260910/qa/main_hall_before_after.png)
- [构建与验证说明](tianyong_festival_hd_20260910/README.md)

总图由36张原生1254×1254分区重绘，以230像素重叠接缝拼合；未把小稿放大后当作最终高清图。保留原城地标，增加道路和广场留白。PNG尺寸、提示词、来源哈希、切片无损重拼已通过校验，整图和主殿、太极广场、南门等重点细节已查看。

## 五类场景

| 场景用途 | 成图 | 实际原生尺寸 |
|---|---|---|
| 主城横版 | [01_main_city_wide.png](qdao_festival_scenes_20260910/final/01_main_city_wide.png) | 2048×768 |
| 仙山登录背景 | [02_login_landscape.png](qdao_festival_scenes_20260910/final/02_login_landscape.png) | 1931×814 |
| 道观庭院背景 | [03_sanctuary_courtyard.png](qdao_festival_scenes_20260910/final/03_sanctuary_courtyard.png) | 2048×768 |
| 森林石桥战斗场景 | [04_battle_forest_bridge.png](qdao_festival_scenes_20260910/final/04_battle_forest_bridge.png) | 1931×814 |
| 战斗入场插画 | [05_battle_entry.png](qdao_festival_scenes_20260910/final/05_battle_entry.png) | 1932×814 |

[场景审阅总览](qdao_festival_scenes_20260910/scene-review-contact.jpg) · [场景详细交付说明](qdao_festival_scenes_20260910/README.md)

主城横版和道观庭院原来共用一张底图，因此保留两个用途入口，使用同一张新版绘画。其余三类各自重绘。场景保存工具实际返回的原生像素，未插值放大或强行拉伸为旧画布尺寸。原参考、实际提示词和制作记录随包保留。

## 使用状态

2026-09-13 已完成本地主城贴图、导航遮罩、前景、五类背景及三个新地点六种外观的客户端接入与部署。新地点使用各自地域自然配色，保留Q版道家与春节／元宵／中秋元素；完整原图都保存在image目录。

进入游戏后点击右侧“地图”或按 M，可前往蓬莱岛、东海渔村、揽仙镇并选择日景或对应节庆外观，也可返回天墉城。客户端与服务端导航同步，四次真实传送（2→3→4→1）、四图WASD及点击寻路、三组换景已通过联机验收；出生误差、导航差异、移动回拉均为0，7张1920×1080实机截图已检查。

[启动游戏.cmd](../启动游戏.cmd) 已使用更新后的 `E:\work\tmp\showcase_player` 客户端，部署289个文件SHA-256全部匹配。旧客户端保留在 `E:\work\tmp\showcase_player_before_festival_20260913_034057`。详见 [六图接入说明](qdao_large_city_maps_20260912/README.md#游戏接入状态)、[接入证据](qdao_large_city_maps_20260912/runtime/integration-delivery.json) 和 [客户端说明](../mmorpg-client/Docs/FestivalRegions.md)。

新六图为原生1254×1254，近景清晰度受原图分辨率限制，与旧天墉城6144分区重绘版本的生产方式不同；没有独立前景的门楼屋顶保持阻挡。旧批次美术发布分支为 `art/festival-city-scenes-20260912`（`0aaed0685ae9e9362e72ae87e20726a7f35b723e`），本轮美术与导航已保存在本地素材提交中；本次不推送混有其他素材任务的image主分支。
