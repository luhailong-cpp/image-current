from pathlib import Path
import json,datetime
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy");p=B/"review/review-cast-limb-fixes-20261003.json";d=json.loads(p.read_text(encoding="utf-8"))
r=next(x for x in d["selectedForSequenceReview"] if x["slot"]=="cast-E-10")
d["attempts"].append(dict(r,status="historical_source_superseded",notes="v3肩部错误挂穗已被v6/v7两步局部编辑取代。"))
r.update(file=(B/"staging/cast-E-10-v7.png").as_posix(),sha256="f047c21f8b004a103d7e6b23aeb391a2f390317489d8300f88be665f92555701",status="prop_corrected_pending_sequence",targetedPropPass=True,notes="实际v7可见：握拳下短黑笔尾接青金尾帽，金环起点贴合尾帽末端，唯一笔青穗悬于袖前；旧肩挂链/穗均已删除。脸、右握持、两靴、左卷及两墨灵布局保留。彩边/整段动态仍未正式通过。")
d["attempts"].extend([dict(slot="cast-E-10",file=(B/"staging/cast-E-10-v6.png").as_posix(),status="structural_intermediate_superseded",notes="第一步去肩挂并补真笔尾/尾帽，尚无笔穗；不得作最终选图。"),dict(slot="cast-E-10",file=r["file"],status="selected_by_actual_attachment_review",notes=r["notes"])])
d["counts"].update(newImages=8,propCorrectionsVisuallyConfirmed=4,unresolvedPropSlots=0)
d["scope"]="5 targeted slots; 8 builtin local edits including newly authorized two-step E10 repair"
d["updatedAt"]=datetime.datetime.now(datetime.timezone.utc).isoformat()
d["latestE10Repair"]={"source":"cast-E-10-v3","steps":["cast-E-10-v6","cast-E-10-v7"],"nativeSize":[1254,1254],"selected":"cast-E-10-v7","attachmentVerifiedByImage":True,"otherCombatFramesRedrawn":False}
d["notes"]=[x for x in d["notes"] if not x.startswith("4 new candidates")]
d["notes"].append("E10 v3/v4/v5失败结论仅为历史；本轮v7根据实际连接图选入，非按最新版本自动通过。")
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
r9p=B/"review/reference09-combat-20261003.json";r9=json.loads(r9p.read_text(encoding="utf-8"));r9["latestTargetedRepair"]={"slot":"cast-E-10","selected":"staging/cast-E-10-v7.png","priorDefectStatus":"resolved_by_actual_local_review","notes":"v3肩挂缺陷系初次只读审查时的历史实况；v7已可见真实笔尾→金环→青穗连续连接。其他68槽审查未因此改写为正式动态通过。"};r9p.write_text(json.dumps(r9,ensure_ascii=False,indent=2),encoding="utf-8")
print("cast-E10-v7 explicit selection saved")

