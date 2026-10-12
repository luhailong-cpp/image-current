# 五行奇谈 · v10 人物与宝宝属性交互预览

2026-09-11。已把人物／四只宝宝的网页预览同步到当前 v10 手绘皮肤，使用正式31张属性切片中的22张原样副本。人物页以身份、六项属性与加点为主体；宝宝页增加四宠头像列表。保留用户确认的无“相性点”版本，采用玉绿、象牙米白、暖金与短红结点缀。

## 查看

在素材仓库根目录启动静态服务：

```powershell
python -m http.server 4345 --bind 127.0.0.1 --directory designs
```

- [人物交互预览](http://127.0.0.1:4345/attribute-panels/v10-preview/?panel=hero)
- [宝宝交互预览](http://127.0.0.1:4345/attribute-panels/v10-preview/?panel=pet)
- [人物2560×1080截图](01-character_2560x1080.png) · [宝宝2560×1080截图](02-pet_2560x1080.png)
- [手机人物](mobile-character.png) · [手机宝宝](mobile-pet.png)

已有该地址的服务时直接复用；若端口被其他服务占用，换一个本地端口并相应修改URL。源入口是 [index.html](index.html)，连同本目录JS、CSS和assets即可独立部署静态预览，无需访问外部图片/CDN。

## 已验证的交互

人物和四宠有独立的待确认分配；支持加减按钮、滑杆、键盘方向键、方案选择、自动分配、重置草稿、确认加点、宝宝返还本次确认点数、参战/休息、说明弹窗、关闭重开。零剩余点禁止继续增加；已确认点数不能通过减号撤回。切换宠物后焦点保持在对应卡片，Escape可关闭面板，重开保留本页草稿。

默认展示待确认分配，方便查看绿色收益；URL加 `&state=clean` 查看未分配状态。状态仅存当前页面内存，刷新恢复入口默认值。示例数据与收益系数沿用旧预览的 [model.js](model.js)，SHA完全一致，未改变加点规则；这不是在线存档或服务端验收。

## 素材与复现

[asset-manifest.json](asset-manifest.json)记录22张本地副本对应的正式来源路径、像素尺寸、SHA-256和九宫格约定。新预览没有改动正式UI切片，也没有重新生图。背景为原生页面底色；人物页没有全身角色和大场景。四宠使用已有正式头像。

页面结构在 `index.html`，外观在 `panel.css`，展示与交互绑定在 `app.js`。`model.js`复制原模型，资产清单保留其来源哈希；`_d_meta.json`为设计版本记录，needs-review指待用户审阅，不代表浏览器检查失败。

安装/迁移通用工具见 [项目安装说明](../../../docs/AI_DESIGN_TOOLS_SETUP.md)。浏览器验证需已安装Node、Playwright及Chrome，本脚本不下载依赖。按当前电脑设置Playwright模块路径：

```powershell
$env:PLAYWRIGHT_MODULE = '<当前电脑node_modules>/playwright'
$env:PREVIEW_URL = 'http://127.0.0.1:4345/attribute-panels/v10-preview/'
node designs/attribute-panels/v10-preview/export-preview.cjs
```

脚本从仓库根目录执行，仅重建本目录标准截图、手机截图和 [validation.json](validation.json)。桌面浏览器逻辑视口1600×675、设备比例1.6，导出2560×1080；手机按390px逻辑宽度检验，PNG仍按设备比例导出。截图是浏览器渲染，不是AI原生画布。

当前验收：浏览器资源与脚本无错误；桌面列无内部溢出；390px竖屏与844px横屏无横向滚动；加点/返还/对象草稿隔离/键盘/焦点检查通过。来源与文件验证见 [delivery-verification.json](delivery-verification.json)。已实看桌面和手机截图，中文、面板层级及按钮区域正常。

## 历史与范围

[v1网页](../index.html)与[v2绘制稿](../v2-painted/index.html)保留供追溯；最新可交互预览使用本目录。正式切片的Unity验收仍以 [原客户端报告](../v2-painted/unity-slices/unity-validation-v10.json)为准，本网页检查不替代引擎或在线服务验收。

新增人物动作、高清主城、扩展场景与后续全库节庆精修由各自任务继续；本次修复仅完成属性网页这个缺口。全项目接手入口见 [交接文档](../../../docs/WUXING_QITAN_HANDOFF.md)。
