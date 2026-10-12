# 聚宝斋 Unity 切图与接入
2026-09-14 已通过 Unity 官方 MCP 完成切图与原生 UGUI 接入。

- **36 张独立 Sprite**：12 张皮肤/装饰与24张商品头像。客户端路径：`Assets/Resources/UI/Ugui/JubaozhaiV1/`。
- 框体、行、按钮、页签和输入框具有显式九宫格边距。标题为固定书法裁片；分类、名称、价格、等级、期限及按钮文字由 TextMeshPro 动态绘制。
- 商品图片中的旧等级和元素徽记以透明区域排除，再用原生圆徽记覆盖；左徽记表达真实商品分类，不编造五行属性。
- 主框复用本项目已认证的 v10 无字透明框；其余切片来自本目录七张最终原图。原稿扁平化遮住的像素没有虚构补画。详见 [切图清单](manifest.json) 与 [接触表](contact-sheet.png)。

## 直接查看
Unity 工程：`E:/work/mmorpg-client`。
进入角色后点击左栏 **聚宝斋 [U]**。独立离线预览请打开 `Assets/Scenes/JubaozhaiPreview.unity` 并按 Play。
预制体：`Assets/Prefabs/UI/JubaozhaiOfflinePreview.prefab`，仅用于显式离线演示。

分类、子类、名称/编号搜索、排序、分页、收藏、商品详情与空状态已接入。正式模式默认空；样例仅在离线预览中加载。公示、拍卖、货架、规则与估价保留可操作入口，但交易、支付与联系卖家服务尚未接入。

## 实际 Unity 截图
- [角色列表 2560×1080](preview-characters.png)
- [宠物列表 1920×1080](preview-pets.png)
- [武器列表 2560×1080](preview-weapons.png)
- [商品详情 1920×1080](preview-details.png)

## 验证与复现
[验收记录](integration-validation.json) · [模型测试](tests.txt) · [官方MCP成功记录](official-mcp-result.json)

官方 MCP 使用项目现有 Unity Relay 与 Assistant 包：实际执行 `JubaozhaiAssetBuilder.Build()` 裁图和 `JubaozhaiUiVerification` 验收。
构建脚本在客户端 `Assets/Editor/Jubaozhai/`，来源默认取同层 `image/designs/jubaozhai-ui`，也可通过 `SourceDirectory` 覆盖。主素材源PNG保持原样，清单记录来源、裁切坐标、Alpha蒙版、九宫格边距与SHA-256。

最终编译通过（280个运行时文件）；Unity内直接执行6项NUnit模型断言，6通过/0失败；同一正式窗口在2560×1080与1920×1080绘制20张截图，原生按钮、搜索、收藏、详情开关、同ID数据更新和到期清理验证通过。未宣称在线交易或PlayMode全链路验收。

