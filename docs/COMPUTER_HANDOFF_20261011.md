# 换电脑继续制作交接 · 2026-10-11

本文件记录当前素材入口、制作范围和保留要求。**提交截止点与远端同步结果由最终同步记录补充；本文不表示 push 已完成。** 旧文档中的历史完成状态、缺图说明和清理要求，与本文件或用户最新要求冲突时，以当前要求为准。

**2026-10-12 最新制作状态：** 用户已要求“边继续做边传吧”，上传窗口确认本批已固定成独立快照。按[恢复制作指令](MAP_PRODUCTION_RESUME_20261012.json)在旧电脑继续三个日景地图，新增素材在本批完成后补传。旧冻结记录和 15/15 就绪清单是本批历史证据，不再代表实时制作目录仍被冻结。下文关于等待迁移后恢复的旧暂停要求由本条新指令覆盖；换机仍须等待包含后续新增素材的最终远端核验。

## 在新电脑拉取

用户于 2026-10-12 最终选择新建私有仓库 `luhailong-cpp/image-current`，以包含当前完整文件的无父提交作为新历史起点，不保留旧 Git 祖先。所有本地文件、作品、源图、脚本和预览均保留；“不要快照”只涉及旧 Git 历史和 `.git` 临时备份，不授权删除本地素材。超过 100,000,000 字节的文件使用 Git LFS，其余文件使用普通 Git。迁移与发布由唯一上传窗口在独立副本处理；三张地图继续制作，新作另行正常快进补传，制作窗口不操作 Git 提交或推送。旧上传队列不恢复。

等待包含后续增量的最终远端提交和 LFS 校验通过后，再在新电脑克隆。先安装 Git 和 Git LFS；Windows 可使用空的 `D:/work/image` 目录，与多数制作脚本一致。以下为已授权的新仓库地址；本文中的命令不代表发布已经完成，提交截止点以最终回执为准：

```powershell
git lfs install
git config --global core.longpaths true
git clone --branch main git@github.com:luhailong-cpp/image-current.git D:/work/image
Set-Location D:/work/image
git lfs pull
```

如果新电脑已有迁移前的旧历史仓库，先保留该目录及本地工作，另选空目录重新克隆；不要用 `reset --hard` 或强制覆盖来接入新历史。只有已经克隆了最终迁移历史、后续正常同步同一历史且本地工作已妥善保存时，才使用：

```powershell
git lfs install
git config --global core.longpaths true
Set-Location D:/work/image
git pull --ff-only
git lfs pull
```

大文件采用 Git LFS，具体范围以最终核验清单和仓库 `.gitattributes` 为准。必须完成 `git lfs pull`，不能把小型 LFS 指针文本当作已下载的素材。账号认证在新电脑自行配置，不从旧电脑复制凭证。

若换盘符或目录，先调整本地运行入口的仓库根路径配置。部分旧脚本、当前地图合同和文档仍含 `D:/work/image`、`E:/work/image`；对应素材通常已在本仓库。**不要全库替换历史生成记录、来源路径、模型字段或哈希。** 根目录 `resume_map_production_20261010.py` 会改写合同和制作状态，不是迁移初始化脚本，不要仅为换电脑重复执行。

## 直接查看原交付

在仓库根目录运行以下命令，然后打开 `http://127.0.0.1:8000/previews/characters-pets-20261010.html`。HTTP 服务可支持读取 JSON 的动作预览；浏览这些页面不需要游戏服务器。

```powershell
python -m http.server 8000 --bind 127.0.0.1
```

| 内容 | 正确入口 |
|---|---|
| 23 位人物与 20 只宠物 | [人物宠物总预览](../previews/characters-pets-20261010.html)，卡片进入各自原动作预览 |
| 20 只宠物动作 | [宠物动作总预览](../designs/creature-combat-20261005/delivery/index.html)及[制作交接](../designs/creature-combat-20261005/delivery/MERGE_HANDOFF.md) |
| 邮件完整绘制原稿 | [活动邮件](../designs/mail-ui-v1/01-mail-event.png)、[系统邮件](../designs/mail-ui-v1/02-mail-system.png)；[原图图库](../designs/mail-ui-v1/gallery.html) |
| 组队、帮会完整绘制原稿 | [组队](../designs/team-ui-v2/team-ui-v2.png)、[帮会](../designs/gameplay-ui/04-guild.png) |
| 聚宝斋七张原稿 | [原图目录与逐页说明](../designs/jubaozhai-ui/README.md)，其中[人物寄售](../designs/jubaozhai-ui/02-characters.png)、[宠物寄售](../designs/jubaozhai-ui/03-pets.png) |
| UI 交互原型 | [邮件](../designs/mail-ui-v1/index.html)、[组队](../designs/team-ui-v2/index.html)、[帮会](../designs/guild-ui-v2/index.html)、[人物与宝宝属性](../designs/attribute-panels/v10-preview/index.html) |
| 节日成图 | [五场景交付](../qdao_festival_scenes_20260910/README.md)、[6144 完整城图](../tianyong_festival_hd_20260910/tianyong_city_master_6144.png) |

聚宝斋交付包含静态原图和切片接入资料，没有声称存在独立 HTML 交互原型。网页原型的本地样例数据也不代表在线游戏业务已接通。

## 继续三张地图

用户已授权旧电脑边制作边上传。先看[恢复制作指令](MAP_PRODUCTION_RESUME_20261012.json)、各分区最新进度和上传窗口的最终远端核验收据。[迁移冻结要求](../MAP_MIGRATION_FREEZE_20261011.json)、[统一冻结就绪记录](MAP_MIGRATION_READY_20261011.json)及各分区 `migration-freeze-20261011.json` 仅为固定捕获批次的历史证据，不表示当前仍冻结或已经上传成功。换机前须核对明确截止点内的新作增量已经发布并核验；换机后从当前采用版本及缺片断点接续。

本轮用户提供的 12 张地图风格参考也已按原始字节归档，见 [参考图索引](../designs/user-references/map-style-20261011/archive-index.json)，不依赖旧电脑临时目录。

先读[当前继续制作指令](../qdao_city_tiles_4k_20260916/builtin_q64_production/resume-production-20261010/README.md)、[机器可读指令](../qdao_city_tiles_4k_20260916/builtin_q64_production/resume-production-20261010/production-resume.json)、[风格入口](../designs/README.md)、[图像配置](../config/image-generation.json)与[逐图来源策略](IMAGE_MODEL_POLICY.md)。

| 当前地图 | 制作入口 | 坐标与分区合同 |
|---|---|---|
| 主城日景 | [主城制作目录](../qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/README.md) | [主城合同](../qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/production-contract.json) |
| 渔村日景 | [渔村制作目录](../qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/README.md) | [渔村合同](../qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/production-contract.json) |
| 八仙岛日景 | [八仙岛制作目录](../qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/README.md) | [八仙岛合同](../qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/production-contract.json) |

每个分区先看自己的最新 `migration-freeze-20261011.json`、`progress.json`、活动原生片映射及交付索引，再接着已有原生片扩展；外部生成缓存的迁移副本以冻结记录所列归档索引为准。固定画布为主城 16×16、渔村和岛各 14×14 个 4096 图块；候选和已验收数量分开统计。5000 人仅完成有条件的静态脚点试验，不代表运行容量已验收；用户已明确此次只做地图美术，不因换机重新开展 Unity 或服务器测试。保留现有坐标、邻接像素与当前风格，不将旧城交付误当成这三张新图已经完成。

## 保留要求与运行边界

- **完整绘制 UI 原稿必须保留。** 邮件两张、组队原稿、gameplay-ui 四张、social-ui 三张、聚宝斋七张及场景选择原稿，都不是程序截图。人物宠物原稿、动作帧、动画、切片、联系表、比较拼图及其他原交付预览也保留。
- 本次用户授权清理的是 **186 张已确认为浏览器或 Unity 运行／测试截图的文件**，见[截图清理记录](screenshot-cleanup-20261011.json)。这不授权按 `preview`、`qa`、`source` 等目录名继续删文件。历史 README 的截图链接可能因此失效；不要据此删除原稿或补回已获准清掉的截图。
- 源码、提示词、生成回执、来源与哈希、当前生产记录和独有在制素材不删除。[恢复记录](asset-recovery-20261010.json)记录了恢复来源；`designs/README.md` 中“邮件 PNG 缺失”是恢复前的旧描述，两张邮件原稿现已恢复。
- 普通静态预览只需浏览器和本地 HTTP 服务。继续图像处理时按具体脚本安装 Python 依赖，如 Pillow、NumPy、SciPy；重新运行浏览器自动验收才需要 Node、Playwright 及浏览器。部分旧验收脚本写死旧电脑安装路径，需要单独配置，不能保证原样直接运行。
- Unity 接入代码引用独立的 `mmorpg-client` 工程；此素材仓库不包含完整客户端与服务器。只有继续相关接入工作时才另行拉取对应工程、按其说明准备 Unity／服务环境，不把离线预览通过当作联机验收通过。
- 历史脚本可能引用旧电脑的生成缓存或聊天记录；这些不是迁移依赖。已落盘交付正常使用，确需重建时另行指定有效源文件，不复制聊天历史、缓存、安装包、SSH 私钥或其他凭证。
- `undefined/roof_object_ownership_trial.py` 是保留的屋顶原生像素归属试验源码，本目录没有它导入的 `workflow.py`，不可作为独立入口运行。不要把它当缓存删除，也不要猜测其运行目录。

旧交接文档中“只留最终图、删除原图／回退版”的概括性规则不再作为本次迁移或后续清理依据。继续工作以前述保留范围和用户最新明确指示为准。
