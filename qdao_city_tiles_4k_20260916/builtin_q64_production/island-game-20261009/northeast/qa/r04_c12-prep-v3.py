from native_work import *
id='r04_c12_p01_02_v3'
x=read(ZONE/'prompts/r04_c12_p01_02_v2.inputs.json'); p=ZONE/'native/r04_c12_p01_02_v2.png';x[0]={'file':p.as_posix(),'sha256':sha(p),'role':'native edit target; interior copied-strip artifacts to repair; preserve outside transition and first145px anchors','generationRecord':p.with_suffix('.png.generation.json').as_posix()};write(ZONE/'prompts'/f'{id}.inputs.json',x)
