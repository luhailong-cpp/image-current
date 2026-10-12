exec((__import__('pathlib').Path(__file__).parent/'audit.py').read_text(encoding='utf-8').split('snapnames=')[0])
j=read(OUT/'inventory.json')
evidence={
'r03_c02':['qa/r03_c02_v7_internal_closure/review.json'],
'r03_c03':['qa/r03_c03_v5_internal_closure/independent_final_internal_closure_review.json','qa/connected-closure-final-v1/closure.json'],
'r03_c04':['qa/r03_c04_v5_internal_closure/closure.json','qa/connected-closure-final-v1/closure.json'],
'r04_c02':['qa/r04_c02_v9_internal_review/review.json'],
'r04_c03':['qa/r04_c03_v5_internal_closure/review.json','qa/connected-r04-r05-final-v1/closure.json'],
'r04_c04':['qa/r04_c04_v4_native_review/visual_review.json','qa/connected-r04-r05-final-v1/closure.json'],
'r05_c03':['qa/r05_c03_v8_internal_closure/review.json','qa/connected-r04-r05-final-v1/closure.json'],
'r05_c04':['qa/r05_c04_v4_internal_closure/visual_review.json','qa/connected-r04-r05-final-v1/closure.json'],
'r06_c03':['qa/r06_c03_v7_internal_closure_20261012/closure.json'],
'r06_c04':['right-current-selection-20261012.json','qa/r06_c04_v1_independent_root_vertical12_review_20261012.json'],
'r07_c03':['qa/r07_c03_v1_owner_native33_review_20261013.json']}
for t in j['tiles']:
 t['internalEvidence']=[dict(meta(BASE/n),scope='archived baseline/current adoption evidence; per-image scope retained; current shared-boundary review separately in pairs/crops') for n in evidence.get(t['tileId'],[])]
 t['currentIncidentPairs']=[p for p in j['pairs'] if t['tileId'] in p['tiles']]
 for m in t['internalEvidence']:
  if m['file'] not in {x['file'] for x in j['inputFiles']}:j['inputFiles'].append(m)
for group in j['mechanicalNativeGroups']:
 related=[p for p in j['pairs'] if all(t in group['tiles'] for t in p['tiles'])]
 group['reviewStatus']='internal_shared_boundaries_pass_perimeter_pending' if group.get('internalSharedBoundaryVisualPassed') else 'reviewed_candidate_repair_required'
 group['currentInternalPairs']=related
 if group.get('internalSharedBoundaryVisualPassed'):
  pp=OUT/'middle_r04-r05_c03-c04_preview1024_NOT_NATIVE.png'
  with Image.open(group['file']) as im:
   preview=im.resize((1024,1024),Image.Resampling.LANCZOS);preview.save(pp);preview.close()
  group['preview']=dict(meta(pp),nativeScale100Percent=False,role='downsampled navigation only, not native evidence')
j['latestModelRuleRead']={'file':'D:/work/image/AGENTS.md','sha256':sha(ROOT/'AGENTS.md'),'readInFull':True,'rule':'2026-10-13 clarification: prefer available free builtin 2.5; allow existing builtin 2.0 fallback. This audit has no generation calls.','appliesToProduction':True}
changes=[]
for m in j['inputFiles']:
 f=Path(m['file']);h=sha(f) if f.exists() else None
 if h!=m['sha256']:changes.append({'file':m['file'],'snapshotSha256':m['sha256'],'finalSha256':h})
j['finalInputRehash']={'checkedFileCount':len(j['inputFiles']),'changedInputs':changes,'stale':bool(changes),'checkedAtUtc':now()}
j['allGroupsStale']=bool(changes)
for g in j['mechanicalNativeGroups']:g['stale']=bool(changes)
j['completedAtUtc']=now()
(OUT/'inventory.json').write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
p=OUT/'review.md';s=p.read_text(encoding='utf-8')
s+='\n已完整重读2026-10-13最新根AGENTS：现有免费入口2.5优先，不可用允许内置2.0继续生产。本独立审核未调用生图；历史暂停字段仅作为原有证据保留，不代表当前全项目停工。\n'
s+=f"\n最终补充核对：{len(j['inputFiles'])}个输入hash，变更{len(changes)}个，stale={bool(changes)}，UTC {j['completedAtUtc']}。每tile内检证据、相关当前接边结论已逐条附入inventory；中间样段新增明确标注NOT_NATIVE的1024导览预览。\n"
p.write_text(s,encoding='utf-8')
print(json.dumps({'summary':j['summary'],'reviewSummary':j['reviewSummary'],'finalInputRehash':j['finalInputRehash']},ensure_ascii=False,indent=2))
