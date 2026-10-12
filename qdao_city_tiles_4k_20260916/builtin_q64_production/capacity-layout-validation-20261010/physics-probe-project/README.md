# 独立碰撞探针（未执行成功）

2026-10-10 实际使用本机 Unity 6000.6.0f1，以 batchmode / nographics 启动本独立工程。Unity 在执行测试方法前因许可证失败退出，日志报告退出码 198。没有可用的碰撞测试结果。

- 日志：[unity-probe.log](unity-probe.log)
- 启动状态与准确错误：[probe-status.json](probe-status.json)
- 待执行脚本：[CapacityCollisionProbe.cs](Assets/Editor/CapacityCollisionProbe.cs)

脚本只用本地 CharacterController 的实际参数（半径 0.38、高 1.8、stepOffset 0.35、skinWidth 0.057、每步下落速度 20），以及源码中远端默认 Cube 和只隐藏 MeshRenderer 的构造方式，在简单平地测试四向接近、擦边、斜向、直接 Transform 重叠。结果必须运行后读取，不能预判有无阻挡。它没有接入正式美术、导航、网络、姓名或 5000 个玩家，也不是完整客户端测试。

本次未打开或修改正式客户端项目。只准备两个内置 module 的最小 Packages 清单，未由 agent 安装任何额外包。当前阻塞是本机 Unity 未取得有效 Editor / headless entitlement；不要将许可证错误解读成客户端代码或地图失败。

正常授权许可证可用后才可重跑。`capacity5000Validated` 始终为 `false`，即使未来该碰撞探针通过也不改变 5000 人验收状态。
