import contextlib,io,json,runpy,sys
from workflow import ROOT,read,write
buf=io.StringIO()
with contextlib.redirect_stdout(buf):
 runpy.run_path(str(ROOT/'request.py'),run_name='__main__')
args=json.loads(buf.getvalue())
old='A horizontal neighbor contributes its rightmost 230 pixels to this crop\'s leftmost 230 pixels; a vertical neighbor contributes its bottommost 230 pixels to this crop\'s topmost 230 pixels.'
new='The sharp bands are already placed in the exact coordinates in image 1. In this tile we usually extend LEFTWARD: a RIGHT neighbor contributes its leftmost 230 pixels to the RIGHTMOST 230 pixels of this crop. An ABOVE neighbor contributes its bottommost 230 pixels to the TOPMOST 230 pixels. Do not move these bands or copy the full adjacent image into the crop.'
args['prompt']=args['prompt'].replace(old,new)
pf=ROOT/'prompts'/f'{sys.argv[1]}_{sys.argv[2]}.prompt.txt'
pf.write_text(args['prompt'],encoding='utf-8')
print(json.dumps(args,ensure_ascii=True))
