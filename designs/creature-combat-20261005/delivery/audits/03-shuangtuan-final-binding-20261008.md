# 霜团貂最终交付绑定核验

2026-10-08 13:38–13:49 UTC，只读复核冻结后的正式交付文件。**未发现技术交付阻塞；动态仅部分验证。** 本次没有重新修图、播放或访问客户端。

- 正式 PNG 68/68：hit 每向6、attack 每向12、cast 每向16；全部1024×1024 RGBA，alpha范围0–255。68个文件SHA及68个像素SHA分别互异。
- 正式 PNG = manifest 68/68 = 逐图 generation record 68/68 = qa/final-visual-review.json 68/68，零不一致。提示词、回执/请求路径及静态验收证据均存在。内置工具的实际型号/质量未知不作为阻塞。
- E12已采用批准的c候选，正式SHA为 `f93f23c85f25a0ec2a4e0f8f03f8c6bde2f5736353a832eb656484a20995f343`。
- 12个WebP及6张接触图均存在，来源SHA匹配当前PNG，WebP帧数匹配；两段MP4实测文件SHA与视频清单一致，全部来源SHA匹配。编码检查报告为passed，视频decodeCheck为passed。HTML已嵌入当前E12 SHA。
- SHA256SUMS.txt的186项全部实测匹配；STATUS、README、MERGE_HANDOFF链接无缺失，文档已同步最终素材和动态限制。validation计数68通过、0缺失、0无效、0重复、0多余PNG。

根表统一集合指纹：`08768398c778113e96eb8859b84ef68e85042709066c27fb3dbcc11bf90a296c`。算法：按hit、attack、cast，再各E、W及升序帧号，只取68个文件SHA，以LF连接且无末尾换行，再取SHA256。早先包含路径并按路径排序的另一算法结果不作为根表指纹。

动态证据 qa/playback-status.json 的68张绑定及videoManifest SHA均匹配当前交付。最终正常速度MP4在Microsoft Media Player做过3次截图抽查，前两次显示相同相位，最后一次为复位/开头；不构成全部过渡和连续流畅度验证。最终0.25倍慢放因播放器窗口消失未完成实看，一次恢复后停止；旧版慢放不计入最终像素验收。准确状态为 `partial-normal-sampled-slow-visual-unverified`，整套可记 `materials-ready-playback-partially-verified`。未绕过HTML浏览器限制，也未重新尝试播放器入口。

以上相对路径以 `D:/work/image/designs/creature-combat-20261005/pets/03-shuangtuan` 为基准。核验仅覆盖最终绑定和已有验收证据，不宣称完整动态或客户端通过。
