# 节庆场景运行时接入

此目录把 final/ 的5个用途成图派生为客户端2560×1080背景合同，包含4张独立绘画。原生图保持原样；派生文件是等比重采样，不代表原生细节提升。

- `01_main_city_wide_2560x1080.png` → `Assets/Resources/UI/Ugui/Native/scene_background.png`，旧主城横版备用净底。
- `02_login_landscape_2560x1080.png` → `Assets/Resources/UI/Ugui/RefreshV8/login_background.png`，登录和选服净底。
- `03_sanctuary_courtyard_2560x1080.png` → `Assets/Resources/UI/Ugui/RefreshV8/sanctuary_background.png`，选角庭院和既有面板预览底图。
- `04_battle_forest_bridge_2560x1080.png` → `Assets/Resources/UI/Ugui/RefreshV8/battle_background.png` 和 `Assets/Resources/UI/Ugui/Battle/Backgrounds/qdao_battle_arena_cloud_terrace_2560x1080_v1.png`，生产战斗净底。
- `05_battle_entry_2560x1080.png` → `Assets/Resources/UI/Ugui/RefreshV8/battle_loading.png` 和 `Assets/Resources/UI/Ugui/Battle/Backgrounds/qdao_battle_entry_loading_2560x1080_v1.png`，战斗入场插画。

客户端对应7个PNG均保留原有路径和整份.meta/GUID。6144可走主城与导航不在此脚本范围内，`World/Tianyong/Backgrounds/tianyong_city_main_64x27_v1.png`也不在本子任务内。

`RoleFlowUi`选角背景优先庭院。原来仅声明、无人调用的`BattleArtCatalog.EntryLoadingPath`现在由`BattlePresenter.PlayEntrance`加载：插画显示0.35秒后在0.45秒内淡出，与原云层和出生光环一起清理，不拦截输入，不等待或改变战斗协议与回合处理。登录标题、人物、按钮和状态文字仍由原生控件独立绘制。

## 适配与复现

以2560:1080为目标，从原画中心取相同比例的浮点区域，Pillow LANCZOS一次等比重采样。

| 原画 | 保留范围（原图像素，左上起） | 等比倍率 |
|---|---|---|
| 2048×768主城/庭院 | x=113.7778…1934.2222，y=0…768 | 1.40625 |
| 1931×814登录/战斗 | x=0.7593…1930.2407，y=0…814 | 1.3267813 |
| 1932×814入场 | x=1.2593…1930.7407，y=0…814 | 1.3267813 |

主城/庭院只裁外缘景物，广场、中央道观和台阶保留。登录与战斗只裁左右各不到1个原像素，入场只裁左右各约1.26个原像素，人物和狐狸完整。所有成图均已目视检查，无标题、进度或按钮等重复UI。

```powershell
python E:/work/image/qdao_festival_scenes_20260910/runtime/build_runtime.py --deploy
python E:/work/image/qdao_festival_scenes_20260910/runtime/build_runtime.py --check
```

`runtime-manifest.json`记录来源哈希、裁切框、等比倍率、部署路径和.meta哈希。`runtime-validation.json`是30项文件/像素合同检查；`runtime-contact.jpg`用于裁切审阅。Unity导入、编译和实际页面截图须以父任务统一验收结果为准，静态检查不等于游戏内验收。

## 战斗台面校准

旧图与新图都曾与旧视频坐标表不吻合，`battle-existing-stage-overlay.jpg`保留本次修正前证据。现已按新石台修正`BattleStage`的视觉位置：仍是每队10槽、前排0–4、后排5–9，列顺序为左下到右上；后排宠物仍使用同列前排位置。队伍归属、协议slot、分配回退、人数合同及战斗业务保持不变。左台较浅，阵列放平并避让桥头金柱；前排预留宠物只向对方方向短移。

`battle-platform-ground.json`是按背景内缘独立手工审定的石台地面多边形，排除河水、桥壁、植被和栏杆。`battle-platform-aligned-overlay.png` / `.jpg`显示绿线台面边界、红蓝主脚点及阴影、橙色预留宠物位。`verify_battle_stage.py`从生产C#读取位置并对独立台面进行检查，不能只靠复制站位表判定通过。

- 20主脚位、20宠物位置与1320个脚点/阴影采样全部在石台内。
- 主脚位最小间距90.139设计像素；实际完整名牌使用256×scale头顶范围，最高顶边y=150.491，低于顶部HUD的140边界。
- 名牌按x±120×scale、脚下40像素的保守范围检查，离命令环中心最近242.139像素，大于235像素半径。
- `BattleUiRoot`背景和单位现在共用固定2560×1080设计根；外围纯色留边。普通16:9不再单独放大背景。新增回归测试构建生产画布，覆盖8种分辨率的画素/脚位重合。
- `BattleStageTests`保留协议/归属/分配语义，旧视频逐数快照改为几何与地面不变量；业务测试原文哈希未变。
- 已有离线编译体检通过：259个运行时C#文件、0错误。Unity NUnit执行和真实截图由父任务统一验收。

```powershell
python E:/work/image/qdao_festival_scenes_20260910/runtime/verify_battle_stage.py
```

上述台面检查针对待机阵型；冲刺/攻击演出按既有业务路径运动，不因此改动战斗逻辑。
