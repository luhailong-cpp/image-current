from workflow import *
from PIL import Image
pid='r12_c12_p24';v='v02';src=ROOT/'native/r12_c12_p24_v01.png'
out=ROOT/'guides'/f'{pid}.native-context-{v}.png'
assert not out.exists()
Image.open(src).save(out)
write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'sources':[{'file':str(src),'sha256':sha(src)}],'operation':'exact whole native edit guide','usableAsFinalArt':False})
