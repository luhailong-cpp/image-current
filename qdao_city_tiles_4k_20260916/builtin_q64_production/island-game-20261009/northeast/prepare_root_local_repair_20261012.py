from native_work import *
import sys
base,new=sys.argv[1:3]
target=ZONE/'native'/f'{base}.png';refs=read(ZONE/'prompts'/f'{base}.inputs.json')
refs[0]={'file':target.as_posix(),'sha256':sha(target),'role':'edit target: localized repair of internal native anchor-strip boundary'}
write(ZONE/'prompts'/f'{new}.inputs.json',refs)
record=read(target.with_suffix('.png.generation.json'));record.update(status='rejected_internal_anchor_material_boundary',pendingIssues=['Internal straight material/shadow/grid boundary requires local imagegen repair.']);write(target.with_suffix('.png.generation.json'),record)
print(json.dumps([r['file'] for r in refs]))
