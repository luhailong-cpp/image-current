from PIL import Image
from pathlib import Path
p=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest/guides/r06_c04_macro_NEAREST_NOT_FOR_ART.png")
Image.open(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/penglai/penglai-natural-stone-wall-trees-v6.png").crop((260,435,370,550)).resize((880,920),Image.Resampling.NEAREST).save(p)

