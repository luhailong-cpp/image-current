from native_work import *
p=ZONE/'native/r04_c12_p02_02.png';x=read(ZONE/'prompts/r04_c12_p02_02.inputs.json');x[0]={'file':p.as_posix(),'sha256':sha(p),'role':'native edit target; extend blue tile rows beyond bottom frame, do not end roof here','generationRecord':p.with_suffix('.png.generation.json').as_posix()};write(ZONE/'prompts/r04_c12_p02_02_v2.inputs.json',x)

