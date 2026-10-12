from native_work import *
import sys
ident,base=sys.argv[1:3]
p=ZONE/'native'/f'{base}.png';x=read(ZONE/'prompts'/f'{base}.inputs.json');x[0]={'file':p.as_posix(),'sha256':sha(p),'role':'native edit target; preserve established composition and repair specified internal discontinuity','generationRecord':p.with_suffix('.png.generation.json').as_posix()};write(ZONE/'prompts'/f'{ident}.inputs.json',x)

