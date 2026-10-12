from native_work import *
src=ZONE/'native/r03_c10_p03_04.png'
refs=read(ZONE/'prompts/r03_c10_p03_04.inputs.json')
refs[0]={'file':src.as_posix(),'sha256':sha(src),'role':'edit target: narrow repair to internal right anchor stripe at x1024; preserve composition'}
write(ZONE/'prompts/r03_c10_p03_04_v2.inputs.json',refs)
rec=read(src.with_suffix('.png.generation.json'));rec.update(status='rejected_internal_anchor_boundary',pendingIssues=['Internal vertical paving/grid/material cutoff at x1024 from y230 to lower edge; requires local imagegen repair.']);write(src.with_suffix('.png.generation.json'),rec)
print(json.dumps([r['file'] for r in refs]))
