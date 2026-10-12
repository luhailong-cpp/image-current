# 豆包接手 Git 提交与上传 · 2026-10-12

## 旧 image 仓库删除同步备用任务

用户随后明确授权另开窗口，把旧 `luhailong-cpp/image` 仓库按当前手动删除情况生成正常删除提交并 push，作为新仓库失败时的备用。已创建新聊天 `01a13097-17db-7f61-9a95-0fa60972c468` 处理此事。本项覆盖历史“不要再尝试旧仓库”的限制，仅允许本次受控正常提交/push，不授权对旧仓库强推、清除历史、付款或恢复旧上传器。旧 image 与新 image-current 为不同目标，不得串用远端。

新聊天使用独立私有 Git/index，只把用户本地已经删除的旧远端跟踪路径从旧远端最新文件树移除，不删除任何现存本地素材，不混入新图的大上传。它须避开新仓库上传进程和锁，唯一窗口依次进行 push。旧仓库曾发生硬配额拒绝；删除提交不会自动释放历史存储。若本次 push 仍被拒绝，保留本地候选、如实说明旧远端未更新并停止重试，不把它宣称为已成功的备用。

用户要求交出详细断点，由豆包接手提交；随后明确要求：先提交当前批次，再继续提交制作期间的新作。此文档交付后，本 Codex 窗口不再启动提交或推送。不要同时运行两个 Git 上传窗口。正在运行的本地构建/检查保持原样，不要停止或重复启动。

## 每小时本地增量提交

用户随后要求 **“这边在同时做的你每隔一个小时也生成一个新提交”**。已创建本对话每小时定时任务 `automation-2`（每小时保存图片制作增量）。这项新授权允许本窗口在豆包按当前副本建立的新基线完成核验后，用独立私有对象库和私有 index 顺序生成本地制作增量提交；此前“本窗口不启动提交”的限制仅对此项本地增量提交更新。首批迁移和推送仍由豆包统一操作，本窗口不接回或重复启动上传器。

有稳定的新增/修改图片才生成提交，无变化不生成空提交。保留图片原始字节，不暂停制作，不恢复用户删掉的目录，不将旧候选接成新祖先；不改变真实工作区 HEAD/index/refs。正在写入的文件留到下一轮。每次真实 commit/tree、父提交和文件清单保存为私有回执，交给唯一上传者按顺序接续；本地提交成功不等于远端已发布。若新基线未完成或另有 Git 操作占用，定时任务等待下一轮。旧自动检查 `automation` 继续暂停。

## 最新指令：当前副本重新提交，旧候选不再发布

用户最新指出 **“我删除了一些目录，你之前的就不对啊”**，并进一步提出 **“豆包是不是要按当前副本提交，丢弃之前的提交呢”**。按最新意图，最终发布应以用户删除后的当前实际目录为源重新捕获和生成提交，丢弃旧候选作为最终发布目标；不再先把过时的旧候选发布成 main，然后才删除目录。本文原“先发布固定旧批次”的执行计划已被这项新范围覆盖。后续制作的新作在新的当前版本后正常快进同步。

旧源清单、旧缺图结论、旧依赖路径及下文 07:58 状态均为历史记录，不代表当前应保留的完整目录。用户已经手动删除的目录不能从旧 Git、旧捕获包、恢复缓存或旧保留清单自动补回；“保留基线全部路径”不适用于这些主动删除。图片保留要求针对当前剩余、用户需要的原图、最终成图和静态预览图片，不再把已删除的旧图片目录纳入必须恢复范围。

2026-10-12 10:25 美国东部时间只读扫描回执：
`D:/work/image/.git/history-prune-image2-20261012/user-deleted-directory-reconcile-20261012T142519Z.json`。
当次扫描相对旧固定源缺失 1747 个路径，其中 1036 个为图片或原生图像格式；同时制作仍在新增文件。这是时间点观察，不是稳定最终捕获。发现 11 个旧顶层目录已不存在：`client_ui_refresh_20260908`、`config`、`previews`、`q_daoist_login_ui_10240_redraw_clear_final_layers`、`qdao_chibi_game_pack_v4`、`qdao_chibi_pets_v1`、`qdao_chibi_roster_v12`、`qdao_original_roster_v13`、`qdao_ui_style_recut_v10`、`quality-review-20261010`、`tianyong_festival_gptimage2_20260910`。不得据旧目录名继续认定它们必须保留或恢复。

同次实际进程观察发现另一个上传进程 PID19836 正在操作 `current-upload-image-current-root-https-v2-20261012`，builder PID4372 已结束且旧 hybrid PASSED report 已存在。此窗口只观察状态，没有启动、停止或修改该上传；旧 07:58 进程与“尚未开始普通上传”描述已过时。接手者必须查实时进程和回执，不能用旧状态重复启动上传器。

唯一上传者应先接管已有进程与状态，停止继续编排过时的最终发布目标，再用当前实际文件重新做稳定捕获、审核和提交；禁止把新目录状态填进旧报告，或在同一固定队列中热换目标。旧对象可以在内容重新核实后作为缓存复用，旧候选提交不得成为新的当前版本祖先。不要删除仍被进程使用的 `.git` 对象/缓存，不碰图片，不对旧 `image` 仓库强推。先查实际远端 refs：尚无正式 main 时，以新的当前副本创建新历史；若 main 已存在，先查其来源与提交身份，由唯一上传者依据本项最新历史替换范围及精确远端状态处理，不覆盖未知他人变更。

最终远端当前文件树及证明必须吻合当前已保留文件、用户手动删除和明确的新作截止点，才可以宣布迁移完成。此窗口不另开 Git 写入流程。

## 最新图片保留与非图片精简范围

用户最新纠正：**“不是预览图，是保留需要的图，最终图和预览图”**，并已明确 **“图不要改啊”**。保留对象是实际图片：需要的原图、最终成图、切片、静态预览图，包含人物、怪物、NPC、主城及此前要求保留的其他素材。图片不改、不删、不覆盖。此前把“预览”理解成必须保留 HTML/JS/JSON 网页预览程序的解释已撤销；不得再以网页预览功能为由额外保留这些非图片文件。用户允许精简非图片文件，范围不限于 JSON。本窗口只进行了依赖检查和交接文本更新，没有删除任何素材。

当前制作与迁移尚依赖的脚本/配置，只在相关操作完成前暂留，以落实用户“先上传当前批次，再上传新作”的要求。已查到主城西南 `assemble.py` 使用选择/坐标记录，东南 `assemble_candidate.py` 使用原图映射，东北 `tile_worker.py` 使用 `coordinates.json`；这些是正在制作新图的输入。固定尺寸裁切成图本身不强制要求 JSON。现成预览 PNG/JPG 可直接看，不必为打开静态图保留网页程序。

继续遵守先发布并核验固定批次、再正常快进增量的顺序。非图片精简作为后续增量处理；不得修改不可变候选和它的校验依据，也不得在进程仍使用时删除其输入。图片保留范围不缩减。把已清理的非图片文件及暂留的在用文件分别记录，不能宣称静态图片交付还必须永久保留所有制作日志、验收报告、HTML/JS/JSON。原清单中已核实且获此项授权删除的非图片文件，不当成意外素材遗漏；图片缺失仍必须调查。

## 必须先完整读取

`D:/work/image/.git/history-prune-image2-20261012/CONTINUE_IN_NEW_CHAT_20261012.md`

上述交接包含完整授权、不可变源清单、工具合同、审核与 SHA、上传/发布/核验步骤。本文件补充该交接之后的实际进展；冲突时以用户最新要求及本文件的新状态为准。下文 W 指 `D:/work/image/.git/history-prune-image2-20261012`。

## 最新实际状态（2026-10-12 07:58 美国东部时间）

- **没有删除本地主城图、图片快照、源图、脚本、预览或其他素材。本窗口也没有清理 `.git`。** 用户说的“不要快照”指旧 Git 历史及 `.git` 临时备份，不是本地图片。不得按目录名如 qa、preview、source 删除任何东西，不覆盖新作。
- 新私有仓库：`luhailong-cpp/image-current`，SSH 为 `git@github.com:luhailong-cpp/image-current.git`。旧 `image` 仓库不强推、不再重试旧配额阻断。
- **普通 Git 尚未上传，main 尚未发布。** 07:57 左右只读 SSH 查询得到 refs `{}`，回执 `W/new-chat-remote-empty-observed-20261012.json`。正式上传前重新查询，不使用陈旧空仓库假设。
- 十个 LFS 大文件已上传，且 **10/10 全部重新远端下载并通过完整 SHA-256 校验**。验证进程 PID9664 已结束，锁已释放。报告 `W/current-ten-lfs-verify-20261012/report.json`，SHA256 `76060d6725c59bf07824f35c265b1d15c8cf97c141b0b2e02bbd6df8f6187f08`。1,315,448,827 字节；此报告不代表普通 Git 发布完成。
- hybrid builder PID4372 仍在运行；当前子进程 PID8656 是 `git fsck --strict --no-reflogs 20929ee0c54b6febe548e52b5c8df4d4394ce57d`。普通 Git pack 已生成，55,200,182,890 字节（约 51.4 GiB）。**最终 report.json 尚未出现，不能批准上传未通过的候选。** 不重启 builder，不删除它依赖的任何对象。观察到的 commit 仅供定位，最终身份必须取 PASSED report 并核实。
- FastGitHub PID42000 仍监听本机 22 端口。一次 SSH 查询发生 `Connection closed by 127.0.0.1 port 22`；随后只读 `ssh -v -T` 已成功认证为 luhailong-cpp，重新查询 refs 成功。未改代理、DNS、全局 Git 配置、SSL 或 SSH 配置。不自动循环重试推送失败。
- 本窗口已阅读并核对上传、finalizer、远端 verifier 及其审核/测试。补充只读代码审核为 `W/verify-current-root-finalized-root-review-20261012.json`；它明确是接手窗口的代码审核，不伪称独立子代理审核。原五例离线测试回执 SHA 与交接一致。
- 本地 `docs/COMPUTER_HANDOFF_20261011.md` 已更新为新 SSH 地址、无旧祖先的新历史、制作继续和新作后续增量。**该修改尚未提交，必须收入后续增量。** 本交接文档本身也收入后续增量。
- 只读初步扫描 `W/increment-preliminary-20261012-v2.json`：当时 103460 个文件，相对原始 102915 个文件新增 545 个、37 个 stat 变化、缺失 0 个。仅为初步 stat 对比，不是最终内容证明/截止点。`increment-preliminary-20261012.json` 第一版存在 Windows DirEntry inode/隐式编码问题，已被 v2 明确取代，不使用第一版判断缺失或变更。

## 原接手执行顺序（历史方案，须按上方最新目标重新制定）

1. 检查实际 PID4372/8656 和输出；等待 `W/current-hybrid-final-main-free-20261012/report.json` 存在且 passed=true。核对 builder SHA、固定源 report SHA、最终 commit/tree、无父提交、对象独立及所有保留证明。失败就保留现场并调查，不能另启旧上传器。
2. 读取 `CURRENT_ROOT_UPLOAD_CONTRACT.txt`、`current-root-upload-ready-for-root.json`、审核/测试及 `current_root_upload_controller.py --help`。使用真实 hybrid report SHA 创建新的 root-approved 输入；remote 固定新 SSH，expected_remote_refs 仅在刚查实为空时为 `{}`，no_paid_operations=true，local_read_only_object_dirs=[]，delete_old_temporary_refs=[]。
3. 运行已审核 controller 的 prepare，再 run `--max-batches 1`。检查服务器精确 ACK、状态和实际速度，然后继续固定队列。每批原始 blob <=512 MiB、pack <1 GiB。不要把新作混入当前固定队列。没有已准备/运行的 controller 上传目录需要续跑；先检查实际磁盘以免其他接手操作改变这一事实。
4. 使用已审核 `build_current_lfs_remote_gate.py` 把上述 10/10 LFS 证明与**实际 hybrid 候选**绑定，不能误用旧 all-LFS 源 commit。按原交接生成明确的最终发布证明/批准字段，禁止付费 LFS、购买 Team、增加预算。
5. 首次 stage ACK 后查询实际 GitHub default_branch。若临时 stage 成了默认分支，采用已审核 `finalize_current_root_default_branch.py` 三阶段：创建 main、API 改 default=main、精确 lease 删除 stage。不要直接删除默认分支；不要伪造 controller published 标志。必须等完整队列 ACK 才发布。
6. 用对应已审核远端 verifier 完成新私有 bare、无 alternates、blob:none 的完整 commit/tree/path/mode/OID 校验，核实真正零 parent。LFS 全量内容校验已有独立报告。不要声称普通 Git 的 50+ GiB 已逐个重新下载。
7. **然后再提交新作增量。** 重新扫描所有实际本地文件，使用私有 index/独立稳定捕获，不 reset 或 checkout 覆盖现场，不使用活跃制作目录的真实 index，不重新接上旧 Git 历史。保留基线全部路径；任何缺失先调查，不自动转成删除。逐文件稳定读取、哈希、前后身份检查，并建立明确截止点及完整增量清单。捕获期间有变化的文件重新捕获或清楚记录尚未同步，不能把不稳定文件算完成。
8. 增量提交的父提交必须是刚核验的新 main（随后批次依次接续），采用正常 fast-forward 推送；如增量较大，按可核验小批处理。新超大文件仍需按无付费范围另行 LFS 证明。不得用旧快照强推覆盖新 main。制作继续产生的后续新作可继续以同样方式提交。
9. 核实最终 main、完整文件范围、LFS 证明及截止点内全部增量，才告诉用户可以新电脑 fresh clone。持续制作的截止点之后内容需要下一次增量，不能说所有未来新作自动完成。旧目录原样保留，在新电脑空目录克隆。

## 禁止事项

不要恢复旧自动检查/旧队列；不要购买 Team 或产生付费 LFS 用量；不要删除或覆盖本地作品；不要停止或重建现有独立构建进程；不要清理仍被构建/上传依赖的 `.git`；不要同时运行两个上传器；不要把凭证、私钥、token、签名下载地址打印或写入文档。

## 最终换机命令（仅在发布及增量核验完成后）

```powershell
git lfs install
git config --global core.longpaths true
git clone --branch main git@github.com:luhailong-cpp/image-current.git D:/work/image
Set-Location D:/work/image
git lfs pull
```

目标目录须为空。旧机器的本地目录和旧克隆保留，不运行 reset --hard。运行仓库携带的验证脚本，并核对最终发布回执指定的 commit 和增量截止点。
