from pathlib import Path
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northeast/r07_c14');S=T.parent/'r06_c14'
for name in ['final_qa_local.py','top_qa_local.py','repair_apply_local.py','repair_ingest_local.py']:
 source=(S/name).read_text(encoding='utf-8')
 source=source.replace("'r05_c14'","'r06_c14'").replace("'r06_c13'","'r07_c13'").replace("'r05_c14.candidate.png'","'r06_c14.candidate.png'")
 target=T/name
 if target.exists():raise RuntimeError('Preserve existing helper: '+str(target))
 target.write_text(source,encoding='utf-8')
print('Prepared tile-local native QA/repair utilities; no art written.')

