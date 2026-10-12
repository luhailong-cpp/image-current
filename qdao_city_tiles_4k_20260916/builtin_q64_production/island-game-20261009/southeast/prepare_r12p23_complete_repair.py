from workflow import *
from PIL import Image
pid='r12_c12_p23';v='v02';src=ROOT/'native/r12_c12_p23_v01.png';out=ROOT/'guides'/f'{pid}.native-context-{v}.png';assert not out.exists();shutil.copy2(src,out);write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'source':str(src),'sourceSha256':sha(src),'operation':'exact copy as full-image edit target; never final art by this operation'})
