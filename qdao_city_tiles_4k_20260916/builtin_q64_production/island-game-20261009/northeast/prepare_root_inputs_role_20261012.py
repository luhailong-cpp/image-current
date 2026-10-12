from native_work import *
import sys
ident=sys.argv[1];inp=ZONE/'prompts'/f'{ident}.inputs.json';r=read(inp)
if len(r[1].get('sources',[]))>1:r[1]['role']='native neighbor reference plate: LEFT=UPPER neighbor, RIGHT=RIGHT neighbor; unscaled1254-square anchors'
write(inp,r)
print(json.dumps({'refs':[x['file'] for x in r],'geometry':patch(ident)},ensure_ascii=False))
