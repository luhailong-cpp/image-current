from pathlib import Path
import json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[1]
for stem in sys.argv[1:]:
 record=R/'records'/f'{stem}.json';data=json.loads(record.read_text(encoding='utf-8-sig'));receipt=json.loads((R/'records'/f'{stem}.receipt.json').read_text(encoding='utf-8-sig'))
 action,direction,number=data['requested_slot'].split('/');frame=int(number)
 source=Path(receipt['nativePath']);native=R/'work'/'root-ground-fix'/f'{stem}-native.png'
 if source.resolve()!=native.resolve():shutil.copy2(source,native)
 subprocess.run([sys.executable,str(R/'tools'/'root_import.py'),'--native',str(native),'--action',action,'--direction',direction,'--frame',str(frame),'--record',f'records/{stem}.json','--replace','--review','two_frame_position_candidate_full_sequence_pending'],check=True)
