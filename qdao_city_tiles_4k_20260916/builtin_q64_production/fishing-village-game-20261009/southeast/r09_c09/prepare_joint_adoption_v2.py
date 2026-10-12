from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
source=(R/'adopt_joints_20261012.py').read_text(encoding='utf-8')
source=source.replace("jointpass-20261012-v1","jointpass-20261012-v2").replace("pids","pids")
source=source.replace("(330,460),(950,1080),(48,145),(1100,1206)","(12,46),(1205,1242),(12,46),(1205,1242)")
source=source.replace("(345,445),(790,890),(48,130),(1020,1140)","(12,46),(1205,1242),(12,46),(1205,1242)")
source=source.replace("not mask[:48].any() and not mask[-48:].any() and not mask[:,:48].any() and not mask[:,-48:].any()","not mask[:12].any() and not mask[-12:].any() and not mask[:,:12].any() and not mask[:,-12:].any()")
source=source.replace("jointpass-v1.png","jointpass-v2.png")
(R/'adopt_joints_20261012_v2.py').write_text(source,encoding='utf-8')

