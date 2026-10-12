from pathlib import Path
import json
B=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy')
p=B/'tools/build_reference09_s_preview.py';s=p.read_text(encoding='utf-8').replace('720','1200').replace('45ms','75ms').replace('>=45','>=75').replace('/45','/75').replace('45*step','75*step');p.write_text(s,encoding='utf-8')
p=B/'review/reference09-S/compare-720.html';p.write_text('<!doctype html><meta charset="utf-8"><title>历史720ms对照已停用</title><p>历史入口已停用。用户最新要求1200ms，每帧75ms。</p><a href="compare-1200.html">当前1200ms对照</a>',encoding='utf-8')
p=B/'review/review-run-S.json';d=json.loads(p.read_text(encoding='utf-8'));d['timing']={'adoptedCycleMs':1200,'frameMs':75,'frameCount':16,'phaseWeightsApplied':False,'previewControls':['normal','slow','pause','frame-step'],'note':'用户最新明确1200ms/16；旧480/640/720/800档仅历史，不作当前入口。'};d['referenceBasedDecision']=d['referenceBasedDecision'].replace('720ms','1200ms');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=B/'review/reference09-S-20261003.json';d=json.loads(p.read_text(encoding='utf-8'));d['timing']['historicalReferenceFrameMs']=45;d['timing']['historicalReferenceCycleMs']=720;d['timing']['frameMs']=75;d['timing']['cycleMs']=1200;d['timing']['comparisonPage']='reference09-S/compare-1200.html';d['timing']['timingAuthority']='最新用户明确覆盖参考角色旧720ms';d['handConclusion']=d['handConclusion'].replace('720ms','1200ms');d['remainingReview']=[s.replace('720ms','1200ms') for s in d['remainingReview']];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=B/'review/grounding-S/README.md';s=p.read_text(encoding='utf-8').replace('720ms对照页已保存','历史720ms对照页已停用，当前1200ms对照页已保存').replace('480/640/720/800ms由主代理统一比较页审阅；720ms仅试播，未采用也未标通过。','用户最新明确跑步1200ms/16=75ms，当前预览仅正常、慢放、暂停和逐帧；旧480/640/720/800档不再作为当前入口。');p.write_text(s,encoding='utf-8')
print('S timing updated to1200ms')

