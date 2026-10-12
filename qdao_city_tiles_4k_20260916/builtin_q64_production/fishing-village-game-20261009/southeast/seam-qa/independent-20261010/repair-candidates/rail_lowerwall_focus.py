from pathlib import Path
from PIL import Image
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast/seam-qa/independent-20261010/repair-candidates')
a=Image.open(D/'r12c08-rail-v2-actual-core-preview/input-actual-cores.png')
a.crop((470,600,790,1254)).save(D/'r12c08-wall-seam-native-focus.png')
a.crop((420,1020,900,1254)).save(D/'r12c08-wall-bottom-native-focus.png')

