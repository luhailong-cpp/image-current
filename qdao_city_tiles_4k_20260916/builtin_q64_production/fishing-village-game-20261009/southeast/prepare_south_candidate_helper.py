from pathlib import Path
p=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast')
s=(p/'r11_c09/native_review.py').read_text(encoding='utf-8')
s=s.replace('ROOT=Path(__file__).resolve().parent',"ZONE=Path(__file__).resolve().parent\nTID=sys.argv.pop(1)\nassert TID in {'r12_c09','r13_c09','r14_c09'}\nROOT=ZONE/TID")
s=s.replace("selection=json.loads((ROOT/'selected-patches.json').read_text(encoding='utf-8-sig'))", "sf=ROOT/'selected-patches.json'\n    selection=json.loads(sf.read_text(encoding='utf-8-sig')) if sf.exists() else {'tile':TID,'internalReady':False,'formalAccepted':False,'patches':{}}")
s=s.replace("'r11_c09-native-candidate-4096.png'", "f'{TID}-native-candidate-4096.png'").replace("'r11_c09-partial-4096.png'", "f'{TID}-partial-4096.png'").replace("'tile':'r11_c09'", "'tile':TID")
s=s.replace("[{'patch':'p12-v1','issue':'Repeated left-neighbor composition; not selected'}]", '[]')
(p/'native_tile_candidate.py').write_text(s,encoding='utf-8')

