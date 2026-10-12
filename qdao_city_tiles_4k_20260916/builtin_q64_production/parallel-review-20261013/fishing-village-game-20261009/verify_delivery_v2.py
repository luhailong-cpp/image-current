from review_tools_v1 import *
import csv

now=datetime.now(timezone.utc)
old=read(OUT/'source-validity-final-v1.json')
progress=SRC/'accelerated-jewelry-approach/progress.json'
acc={s['tile']:s for s in read(progress)['currentAdoptedCandidates']}
rebinding=[]
for d in sorted(OUT.glob('G0[1234]-*')):
    m=read(d/'manifest-v1.json')
    for s in m['sources']:
        if '/accelerated-jewelry-approach/' not in s['file'].replace('\\','/'):continue
        current=acc[s['tile']]
        rebinding.append(dict(group=d.name,tile=s['tile'],pinned_file=s['file'],current_file=current['file'],pinned_sha256=s['sha256'],current_sha256=current['sha256'],same_adopted_source=Path(s['file'])==Path(current['file']) and s['sha256']==current['sha256'] and sha(current['file'])==s['sha256']))
assert all(x['same_adopted_source'] for x in rebinding)
validation=dict(old)
validation.update(checked_at_utc=now.isoformat(),supersedes=record(OUT/'source-validity-final-v1.json'),raw_metadata_changes_retained_as_history=old['changed_selection_metadata'],refreshed_selection_records=[record(progress)],actual_adopted_source_rebinding=rebinding,stale_groups=[],changed_selection_metadata=[],metadata_rebinding_note='Earlier conservative check marked G02/G03 stale because acceleration progress.json changed. Re-read its explicit currentAdoptedCandidates: every reviewed tile path+SHA is identical. Partial working selections and NE active candidate metadata remained unchanged. The checks are refreshed for these same pinned pixel sources only.')
for c in validation['review_inputs']:
    c['actual_sha256']=sha(c['file']);c['pixels_unchanged']=c['actual_sha256']==c['expected_sha256']
validation['all_review_pixel_hashes_current']=all(x['pixels_unchanged'] for x in validation['review_inputs'])
validation['stale_groups']=sorted({c['group'] for c in validation['review_inputs'] if not c['pixels_unchanged']})
crop_checks=[]
for d in OUT.glob('G0[234]-*'):
    for p in d.glob('*100pct.png.trace.json'):
        if '-sheet-' in p.name or p.name in ['V-segments-sheet-100pct.png.trace.json','H-segments-sheet-100pct.png.trace.json','junctions-sheet-100pct.png.trace.json']:continue
        t=read(p);r=t['output'];a=record(r['file'])
        crop_checks.append(dict(file=r['file'],sha_matches=a['sha256']==r['sha256'],dimensions_match=a['dimensions']==r['dimensions'],operation=t['operation'],global_box=t['global_box']))
assert len(crop_checks)==46 and all(c['sha_matches'] and c['dimensions_match'] for c in crop_checks)
validation['reviewed_crop_integrity']=crop_checks
validation['all_46_crops_intact']=True
write(OUT/'source-validity-final-v2.json',validation)

coverage=read(OUT/'coverage-snapshot-v2.json')
coverage.update(createdAtUtc=now.isoformat(),supersedes=record(OUT/'coverage-snapshot-v2.json'),historicalProductionMetadataRecheck=coverage['productionMetadataRecheck'],productionMetadataRecheck=dict(checkedAtUtc=now.isoformat(),refreshedPartialSelection=record(OUT/'r08-c09-selection-refresh-v1.json'),reviewSourceValidity=record(OUT/'source-validity-final-v2.json'),note='r08_c09 selection refreshed to two cores; earlier stale row superseded. Inventory remains a fixed snapshot.'),snapshotNotLive=True)
write(OUT/'coverage-snapshot-v3.json',coverage)
with (OUT/'coverage-snapshot-v3.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(coverage['coordinates'][0].keys()));w.writeheader();w.writerows(coverage['coordinates'])

lookup={r['coordinate']:r for r in coverage['coordinates']}
special={tuple(sorted(p)):s for p,s in [
 (['r04_c11','r04_c12'],'east_edge_four_segments_locally_passed_north_corner_needs_FV_SEAM_002'),
 (['r05_c11','r05_c12'],'needs_AI_material_repair_FV_SEAM_001'),
 (['r05_c11','r06_c11'],'south_edge_three_of_four_segments_locally_passed_missing_p11'),
 (['r10_c07','r10_c08'],'four_segments_and_available_junctions_locally_passed_formal_pending'),
 (['r11_c07','r11_c08'],'needs_AI_material_repair_FV_SEAM_003')
]}
edges=[]
for r in coverage['coordinates']:
    for dr,dc,axis in [(0,1,'vertical'),(1,0,'horizontal')]:
        rr,cc=r['row']+dr,r['column']+dc
        if rr>14 or cc>14:continue
        n=lookup[f'r{rr:02d}_c{cc:02d}']
        if r['assignedOwner']==n['assignedOwner']:continue
        key=tuple(sorted([r['coordinate'],n['coordinate']]))
        edges.append(dict(tiles=list(key),owners=[r['assignedOwner'],n['assignedOwner']],axis=axis,coverage=[r['coverageStatus'],n['coverageStatus']],status=special.get(key,'neighbor_native_source_missing_or_incomplete_not_accepted'),formal_pass=False))
assert len(edges)==38
write(OUT/'cross-area-boundaries-v1.json',dict(created_at_utc=now.isoformat(),boundary_count=38,executable_boundaries_reviewed=5,remaining_missing_neighbor_boundaries=33,edges=edges,additional_same_owner_checks='G03 r06_c11/c12 east edge and all available central junctions; G02 r04_c12/r05_c12 north seam extension with new FV-SEAM-002.',central_four_quadrant_junction='x28672,y28672: missing native neighbors, not accepted',scope='Owner seams include the six acceleration coordinates; coverage is deduplicated. No final map acceptance.'))

summary=read(OUT/'review-summary-v1.json')
summary.update(created_at_utc=now.isoformat(),supersedes=record(OUT/'review-summary-v1.json'),coverage_table=record(OUT/'coverage-snapshot-v3.json'),source_validity=record(OUT/'source-validity-final-v2.json'),cross_area_boundary_inventory=record(OUT/'cross-area-boundaries-v1.json'),all_review_pixel_sources_unchanged=validation['all_review_pixel_hashes_current'],all_reviewed_crops_intact=True,stale_groups=validation['stale_groups'])
write(OUT/'review-summary-v2.json',summary)
txt=(OUT/'REVIEW-RESULT-v1.txt').read_text(encoding='utf-8')
txt=txt.replace('独立收尾检查 v1','独立收尾检查 v2').replace('coverage-snapshot-v2','coverage-snapshot-v3').replace('review-summary-v1','review-summary-v2').replace('source-validity-final-v1','source-validity-final-v2')
txt+=f'''\n最终复核：{now.astimezone().isoformat()}（详见UTC时间记录）。全部审阅像素源SHA未变，46张裁片尺寸/SHA完整。
加速区progress元数据曾变化，旧v1来源检查已保留其过期标记；重新读取当前采用文件路径和SHA均一致，本v2仅重绑定同一批像素，不把旧结论套给新版本。
跨制作区边界共38条：5条有足够现存边缘可作本批局部检查，33条缺邻源/完整边缘，逐条见cross-area-boundaries-v1.json。局部通过不等于整块正式通过。
'''
(OUT/'REVIEW-RESULT-v2.txt').write_text(txt,encoding='utf-8')
print(json.dumps(dict(all_review_pixels_current=validation['all_review_pixel_hashes_current'],all_46_crops_intact=True,stale_groups=validation['stale_groups'],boundary_inventory_count=len(edges),review_summary=str(OUT/'review-summary-v2.json')),ensure_ascii=False))
