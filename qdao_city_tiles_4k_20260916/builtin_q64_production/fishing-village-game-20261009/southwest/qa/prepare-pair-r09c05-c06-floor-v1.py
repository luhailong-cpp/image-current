import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
from PIL import Image
Z=Path(__file__).resolve().parents[1];QA=Z/'qa';source=QA/'pair-r09c05-c06-v1-context-native.png';im=Image.open(source);box=[3585,2305,4839,3559];out=QA/'pair-r09c05-c06-floor-source-native-v1.png';assert not out.exists();im.crop(box).save(out)
ref=lambda p:{'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
rec={'file':ref(out),'source':ref(source),'contextBox':box,'pairTileContextBox':[3470,2190,4724,3444],'globalContextBox':[19854,34958,21108,36212],'dimensions':[1254,1254],'operation':'exact native integer crop only','nativePixelsResampled':False,'findings':[{'id':'J01','localPoint':[621,440],'note':'upper broken grout segment across shared seam'},{'id':'J02','localPoint':[601,625],'note':'lower broken grout segment across shared seam'}]}
Path(str(out)+'.derivation.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8');print(ref(out))
