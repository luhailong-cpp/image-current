# 烛翎 W 方向独立静态与来源复核 · 2026-10-08

执行者：root/audit_pet_batch_a。范围仅为下列当前正式帧。通过实际 view_image 查看逐张像素，并读取逐图记录、实际提示词/回执、原生来源及 SHA；未以文件计数替代视觉判断。

**本记录仅为静态顺序与来源复核，不替代正常速度或0.25倍连续播放，不代表游戏客户端验收。** 后续替换任一图片后，须按新SHA重新复核，不能沿用此结论。

## W 普攻 08→09→10

实际查看时间：2026-10-08 10:43 UTC。

三张均保持两翼、两足、短扇尾、真实后背/后脑朝左上及原有冠饰、绢带和坠饰。W08近翼前收、另一翼高举；W09近翼撤回侧后，头肩回收；W10双翼重新展开为较低张翼。静态顺序可辨认前收→撤回→重开，没有发现当前像素的第三翼问题。

W08已真实替换为下面的新SHA。先前三翼拒稿和旧SHA只属于历史，不再要求依据旧稿修当前图。W09采用原窗口其他新来源，并非本审计执行者制作的辅助候选。

三张均1024×1024 RGBA、Alpha范围0–255。检查时总manifest与逐图记录SHA全部匹配。W08/09的记录位于 records/attack/W/08.generation.json、09.generation.json；W10在图旁sidecar。对应prompt、receipt、原生图均存在且原生SHA复算一致。统一整画布缩至820并置于1024画布(102,102)，没有逐帧脚点对齐。缺少W08/09图旁sidecar不是来源遗漏，manifest已正确索引records目录。

## W 施法 12→13→14→15→16→01

实际查看时间：2026-10-08 11:11 UTC。

六张静态相位可接受，均保持两翼两足、短尾、后背朝向和原有饰物。13进入收势，15有小幅翼尖回弹，16返回与01接近的备战姿。12→13画右翼有一次上提，作为悬浮回稳中的拍翼变化可理解，不是双翼单调下降；未发现额外肢体、方向翻转或主体裁切。

新W13/15/16均为1024×1024 RGBA、Alpha0–255，图旁 .png.generation.json 与正式图SHA匹配。宠物目录内复制的root-assist-20261008原生证据、prompt、receipt均存在；derivedFrom SHA与辅助原生图及复制后的原生记录复算一致。统一820缩放+(102,102)留边记录正确，actualModel/actualQuality未披露，仍为null，不视为阻塞。

## 被检像素绑定

路径相对于 D:/work/image/designs/creature-combat-20261005/pets/01-zhuling。

| 文件 | SHA256 |
| --- | --- |
| runtime/attack/W/08.png | f4c7666f855b97339b0c89925d6264d2a284a43efd91c235e2acc7612cd178b9 |
| runtime/attack/W/09.png | f6ab56264683a03e942ed4f3878ead8ee7e923fb3100ee4f2777dd1f69531382 |
| runtime/attack/W/10.png | 6d9b38f72ad822877da72cce591221187eda6a963a03d13733fdde6acfe39887 |
| runtime/cast/W/12.png | b0a74ecdbac47da411d1b7992cb5ef35e080bec4ff8d2e0b289954a49796a368 |
| runtime/cast/W/13.png | 88cf391198b467a2b70a05d2b56d9648e42e9f19a13fba34c49c1cfd2a83fe3d |
| runtime/cast/W/14.png | f97f9cccfdc8274f56568efce37e43455419a212acf138cf2c552e41bd27c08c |
| runtime/cast/W/15.png | d73a9f42e9e81c6595e9bde786a30c2cc10791d1320c61d44bdb773ad44176c6 |
| runtime/cast/W/16.png | 82482184d10916085730c9e9991af37029f9a9ade1038311b8a2c2fad134313d |
| runtime/cast/W/01.png | ae5ec0e9429dfdb2a967918113e12975f2e726ac3a4c9489466e6e3a785e5867 |

写本记录前已再次只读复算以上9张SHA，与实际查看时的版本相同。没有修改任何宠物正式目录、图片或生成记录。

## 收尾技术复核补记 · 2026-10-08 11:47 UTC

本节是只读技术/文档复核，不是新增静态或动态目视验收。检查期间owner仍在写最后的播放记录与清理结果，因此不提前标为全部交付完成。

- 总manifest版本为2026-10-08T11:06:22.341738+00:00，索引68张正式帧；逐一重算，68个PNG SHA全部匹配manifest，68份generationRecord均存在且正式SHA匹配。validation同版本为passed，无缺帧/重复/来源问题。
- root辅助补出的cast W13/15/16都在总manifest中，指向正式runtime图旁 .png.generation.json；正式图SHA与本报告前表一致。逐图prompt、receipt及原生证据已复制到宠物自身prompts/records目录，均存在。
- 正式播放器preview/index.html引用runtime帧，不包含delivery/assist或helper预览引用。三张图derivedFrom.file保留辅助原生图的绝对路径，是来源文字证据，并非播放器运行依赖；正式图及其说明不需要从helper预览加载。
- **当前确切metadata残留：** 三张正式sidecar仍继承原生候选的status=candidate-for-owner-review、writeScope=delivery/assist/01-zhuling-cast-W only; formal pet runtime and manifest not modified，以及visualReview待owner播放审核。总manifest的visualStatus也仍写候选/待最终播放。前者writeScope在正式导出后已经不准确，需owner更新正式导出状态/采用范围/最终验收索引；records内root-assist-native原生历史记录应保留当时真实状态，不回写旧史。
- README与MERGE_HANDOFF已存在，指向正确的正式runtime、manifest和本地preview，声明客户端未接入。但STATUS.md尚不存在，README中的状态链接未完整。
- manifest指定的qa/visual-review.json尚不存在，无法核对最终视觉记录的68个SHA。现有qa/final-static-review.json只覆盖40张静态帧，不能代替最终六组连播记录或68张最终像素绑定。
- MERGE_HANDOFF提到cleanup.json，检查时该文件尚不存在，不能声称最后清理记录已经完成。

结论：正式68张图片、总清单SHA与逐图来源链已齐且相符；最终视觉记录、STATUS、清理记录及三张正式sidecar采用状态仍待owner收尾。没有据历史拒稿重复要求修当前图片，没有修改宠物目录或删除原生图。




## 主窗口最终补充：2026-10-08T11:56:38.808493+00:00

此前11:47 UTC的待收尾项现已全部解决。重新计算全部68张正式PNG，与当前manifest及qa/visual-review的68项SHA逐一一致；README、STATUS、MERGE_HANDOFF、validation及正式预览齐全。W13/15/16正式sidecar已为adopted-final-runtime，writeScope和最终视觉引用正确。当前正式预览只引用runtime，不依赖辅助预览。来源prompt、receipt及原生文字记录齐全。最终记录的播放方法为原窗口浏览器正常/慢放抽样和六个逐帧控件操作，主窗口本次仅做文件/SHA验证，不新增动态实播声明。

逐项证据见../assist/01-zhuling-cast-W/adoption-verification.json；较早阶段的待审核结论为历史快照，不代表当前状态。
