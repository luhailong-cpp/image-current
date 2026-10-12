import json
from pathlib import Path
S=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest')
d=json.loads((Path(__file__).parent/'receipt-discovery.json').read_text(encoding='utf-8'))
for x in d['receipts']:
 if not x.get('image'): continue
 print(x['image']['sha256'][:10], str(Path(x['receipt']).relative_to(S)), 'REJECT' if x['explicitRejected'] else '')
