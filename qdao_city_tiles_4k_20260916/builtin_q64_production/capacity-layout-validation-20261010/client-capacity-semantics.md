# 5000 人容量语义：客户端与服务端只读审查

审查日期：2026-10-10。对象为 `D:/work/mmorpg-client` 及其 README 指向的同级服务端 `D:/work/mmorpg`。这份报告核对当前磁盘源码，不证明线上运行版本、运行配置或 5000 人压测结果。

**修正结论：上一轮 5/6 世界单位的方形站位间距、1.45 的地面检测半径和 20% 留空是自选视觉实验参数，不是客户端或服务端的容量规则。因此，“某档没有排满 5000 个格点”不能推出必须扩图或重画。用户要求是同一地图分散 5000 人，不是每个手机同时绘制 5000 人。**

## 真实碰撞和视觉占地不是一回事

| 项目 | 源码/配置事实 | 容量含义 |
|---|---|---|
| 本地玩家 | CharacterController 半径 0.38、高 1.8；skinWidth 约 0.057 | 不是 5/6 单位的实体占地 |
| 远端玩家 | ActorWorld 用默认 Cube 创建；精灵替换只关 MeshRenderer；检查路径没有移除远端 BoxCollider | 不能先假设所有玩家都是 0.38 圆，也不能先假设玩家互相穿透 |
| 远端移动 | 每帧直接插值 Transform；本地玩家使用 CharacterController.Move | 本地物理阻挡与远端网络位置可以不一致，必须小规模运行复现 |
| 阴影 | SpriteRenderer，宽 2.9、纵横比 0.66，即约 2.9×1.914 | 只是画出来的阴影，不是 2.9 的碰撞直径 |
| 人物 | 512/52 或 1024/104，画框约 9.846 世界单位 | 画框包含透明区；精灵、武器重叠不等于脚点非法 |
| 姓名 | 默认 em 高 1.25，禁止换行、允许溢出，底板随真实文字宽度变化；近景另有像素高度限制 | 不能用固定 5 或 6 保证任何姓名都不重叠 |

证据：

- [实际玩家配置](D:/work/mmorpg-client/Assets/Resources/World/Tianyong/TianyongMapConfig.asset:21)，[本地替换碰撞体及参数](D:/work/mmorpg-client/Assets/Scripts/World/Tianyong/TianyongPlayerController.cs:145)，[Move 调用](D:/work/mmorpg-client/Assets/Scripts/World/Tianyong/TianyongPlayerController.cs:468)。
- [Cube 创建](D:/work/mmorpg-client/Assets/Scripts/World/ActorWorld.cs:169)，[远端插值](D:/work/mmorpg-client/Assets/Scripts/World/ActorWorld.cs:393)，[仅隐藏 MeshRenderer](D:/work/mmorpg-client/Assets/Scripts/World/QdaoBoySpriteAnimator.cs:180)，[只对本地添加控制器](D:/work/mmorpg-client/Assets/Scripts/World/Tianyong/TianyongMapRuntime.cs:213)。ActorWorld 根 localScale 在 105 行设为 one；标准生成路径没有另设远端缩放。默认 Cube 的 BoxCollider 行为仍需实际 Unity 验证，不能仅凭阅读保证所有场景都相同。
- [阴影宽度](D:/work/mmorpg-client/Assets/Scripts/World/QdaoBoySpriteAnimator.cs:80)，[阴影缩放](D:/work/mmorpg-client/Assets/Scripts/World/QdaoBoySpriteAnimator.cs:669)，[画框世界高度](D:/work/mmorpg-client/Assets/Scripts/World/QdaoBoySpriteAnimator.cs:40)。
- [姓名大小及溢出](D:/work/mmorpg-client/Assets/Scripts/World/WorldNameplate.cs:35)，[底板随字宽变化](D:/work/mmorpg-client/Assets/Scripts/World/WorldNameplate.cs:255)，[姓名近景缩放](D:/work/mmorpg-client/Assets/Scripts/World/WorldLabelBillboard.cs:101)。

本地导航检查的是静态可走格；没有将其他玩家登记为每人占用 5×5 或 6×6 的网格。[静态导航构建与 IsWalkable](D:/work/mmorpg-client/Assets/Scripts/World/Tianyong/TianyongNavigationGrid.cs:60)、[防穿对角障碍](D:/work/mmorpg-client/Assets/Scripts/World/Tianyong/TianyongNavigationGrid.cs:164)不能被解读为玩家互斥站位协议。

服务端所读移动主路径将速度积分后交给静态 NavMesh raycast，未发现逐玩家两两阻挡判定：[movement.cpp](D:/work/mmorpg/cpp/libs/services/scene/spatial/system/movement.cpp:53)、[nav_query.cpp](D:/work/mmorpg/cpp/libs/services/scene/spatial/system/nav_query.cpp:86)。另有 DtCrowd 旧入口，参数半径 0.6，但本次检索仅发现 try_get、addAgent 和类型定义，未找到配套创建/逐帧 update；不能据此宣称已启用人群避让，更不能推导 5/6 间距。[旧 Crowd 入口](D:/work/mmorpg/cpp/libs/services/scene/spatial/system/scene_crowd.cpp:23)。

## 同图人口与每端附近角色数量

服务端存在 AOI（附近关注列表）机制：

- 默认关注列表 100，代码允许 20～200；有效值取客户端意愿与场景压力上限的较小值。[常量](D:/work/mmorpg/cpp/libs/services/scene/spatial/constants/aoi_priority.h:97)、[容量函数](D:/work/mmorpg/cpp/libs/services/scene/spatial/system/interest.cpp:39)。
- 玩家创建设视距 10 世界单位，CanSee 检查位置距离。[创建视距](D:/work/mmorpg/cpp/libs/services/scene/player/system/player_lifecycle.cpp:2409)、[距离判断](D:/work/mmorpg/cpp/libs/services/scene/spatial/system/view.cpp:40)。
- AOI 下发 create/destroy，客户端按收到的实体生成/删除，并未在该收包路径再次限制为 100 或 200。[AOI 通知](D:/work/mmorpg/cpp/libs/services/scene/spatial/system/aoi.cpp:158)、[客户端创建](D:/work/mmorpg-client/Assets/Scripts/Game/GameClient.cs:1777)、[客户端删除](D:/work/mmorpg-client/Assets/Scripts/Game/GameClient.cs:1790)。

**100/200 是所读源码的关注列表设置，不是已经验收的客户端 GameObject 数量硬上限。** 关注列表满时的优先级替换只看到列表 erase；本次读取的通知流程没有证明替换旧实体一定同步发 destroy。相同 hex 内移动直接返回、反向关注列表更新和通知对应关系也需端到端测试。[列表替换](D:/work/mmorpg/cpp/libs/services/scene/spatial/system/interest.cpp:98)、[网格更新](D:/work/mmorpg/cpp/libs/services/scene/spatial/system/aoi.cpp:62)。未确认客户端期望数量的设置入口、场景压力更新来源及线上参数。

源码虽有 `kMaxPlayersPerScene=1000`、`kMaxServerPlayerSize=2000`，本次检索在生产代码仅找到常量定义，使用点在测试里，故不能宣称当前同场景硬限制为 1000。[常量](D:/work/mmorpg/cpp/libs/engine/core/node/constants/node_constants.h:5)。Go 场景管理器默认 2000 是频道自动扩容阈值，自动扩容默认关闭；阈值不等于准入硬上限。[配置](D:/work/mmorpg/go/scene_manager/internal/config/config.go:293)。当前运行服的实际准入条件仍未验收。

因此合理验证目标是：5000 人保持相同地图与频道并分散活动，各端按附近对象同步；同时测试出生点、擂台、商店门口等热点。不能通过分流到多个频道后合计 5000 来替代“同图同频道 5000”。

## 世界尺寸和图片像素

旧实装画面 6144×6144 对应 worldRect=(50,0,300,300)，密度为 20.48 px/u；静态导航采样为 2 世界单位。[旧范围](D:/work/mmorpg-client/Assets/Scripts/World/Tianyong/TianyongPaintedCity.cs:31)、[导航格](D:/work/mmorpg-client/Assets/Scripts/World/Tianyong/TianyongPaintedCity.cs:58)。客户端与服务端坐标只交换轴，不额外缩放：[坐标转换](D:/work/mmorpg-client/Assets/Scripts/World/WorldCoordinateConverter.cs:28)。现有分块加载器还拒绝 worldRect 与旧范围不一致的清单：[范围检查](D:/work/mmorpg-client/Assets/Scripts/World/Tianyong/CityTileStreaming.cs:90)。

三份新生产合同均为 `worldSize:null`、`capacity5000Validated:false`。65536 是美术像素规格，不能除以臆定的 300 世界单位后把 218.45 px/u 当成已生效密度，也不能把图片更清晰当成容量已增加。整体调大世界会同步放大建筑、门洞，仍须审查人物比例。村岛面积各为主城 0.75 的关系也只是世界尺寸规划关系，不能替代各图的通行检查。

## 可执行的验证标准

1. **脚点合法、通路可达：** 用最终实际导航和障碍边界验证出生点、南北门、官府、道馆、塔、擂台、商店及八处仙居互通；按实际控制器半径考虑边界余量。人工保守可见地面用于找疑点，屋顶遮挡造成的图像断开不直接等于导航断路。
2. **碰撞语义先验证：** 在独立最小 Unity 工程复现半径 0.38 的本地 CharacterController 与默认远端 Cube，四向接近、斜向擦边、直接 Transform 重叠；记录 Collider、layer、scale、skin、stepOffset。此前仅静态源码审查，未声称已通过。
3. **尺寸只做条件公式：** 若明确选择所有角色为互斥半径 r 圆盘，两脚点中心距理论至少 2r=0.76；单人净通道理论至少 2r、两人并行理论至少 4r=1.52，再加实测余量。这不是现有客户端规则，也未计远端方盒。现有半径 0.38 对半宽 0.5 的盒子，正向几何接触约 0.88，受旋转、skin、step、同步影响，应以小探针实测为准。不能反向替换成“0.76 间距必然可玩”。
4. **视觉舒适度另验：** 以真实人物、长姓名、武器、宠物和镜头尺度查看若干局部密度；允许阴影或精灵重叠与否是玩法/显示决策。可以保留 5/6 档作为宽松视觉比较，但不得将其设为容量必要条件。
5. **附近显示链路另验：** 50/100/200 个附近实体逐步进出范围，确认创建、离开、优先级淘汰、不残留、点击目标、名称开关，并在目标手机记录帧时/内存。少量角色测试可验证机制，不能证明 5000 同场景性能。
6. **5000 运行容量另验：** 记录同 sceneId/lineId 的 5000 在线且分散移动，服务器 tick、延迟、消息量、错误、每端附近对象数与目标手机表现；再测试热点聚集。当前未运行此项。

## 审查状态与制作决策

本次只读了客户端/服务端源码、配置和已有静态验证资料，未修改正式客户端、服务器、图片或生产参数；未启动大负载。当前证据支持先验证碰撞语义与接入尺度，再决定是否需要局部通道改动。**不能因为自选网格排不下，就要求整图重画；也不能保证当前美术无需任何局部调整。**

本目录上一轮 summary/results 数值仍然描述它们自己的 5/6 参数实验，无需把数值删除；解读必须限定为“该自选视觉网格的 first tested scale”，而非“5000 人最小地图尺寸”。`capacity5000Validated` 仍为 `false`。后续独立物理探针只验证碰撞设置，仍不改变这个容量验收状态。

## 独立物理探针的实际尝试

本报告之后，已在本目录 `physics-probe-project/` 建立最小工程并实际启动本机 `D:/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe`（batchmode、nographics）。**Unity 在执行测试脚本之前因许可证失败退出，日志报告退出码 198。** 日志明确写有 `No valid Unity Editor license found. Please activate your license.`，并报告 `com.unity.editor.headless` entitlement 未找到。

[实际日志](physics-probe-project/unity-probe.log)、[准确状态](physics-probe-project/probe-status.json)、[待执行脚本](physics-probe-project/Assets/Editor/CapacityCollisionProbe.cs) 已落盘。未生成 `probe-results.json`，没有可引用的碰撞运行结果；此前远端 Collider 保留仍是源码推断。本次未打开正式客户端，未安装额外包，也未运行大负载。该许可证阻塞不能解释为地图或客户端代码失败。
