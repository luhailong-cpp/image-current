from pathlib import Path
import json
b=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy')
for key in ['run-N-01-v3','run-N-09-v3','run-NW-04-v2','run-N-04-v4','run-N-12-v3','run-NW-12-v2']:
 p=b/'staging'/(key+'.png.generation.json');d=json.loads(p.read_text(encoding='utf-8-sig'));rec=json.loads((b/'provenance'/(key+'.tool-result.json')).read_text(encoding='utf-8'))
 d['generatedAtEvidence']='Registration after interrupted prior turn; actual exact generation timestamp not disclosed. Host original already existed earlier; this is not a fresh image generation time.'
 d['evidence']['toolResultFile']='provenance/'+key+'.tool-result.json';d['evidence']['recoveryEvidence']=rec['recoveryEvidence'];d['evidence']['returnedFields']=rec['returnedFields']
 if not rec['returnedFields']:d['evidence']['recoveredNativePath']=d['evidence'].pop('toolReturnedPath')
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

