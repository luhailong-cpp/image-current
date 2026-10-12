import sys,json,argparse
from pathlib import Path
sys.dont_write_bytecode=True
SW=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(SW))
import native_pipeline as n
a=argparse.ArgumentParser();a.add_argument('tile');a.add_argument('action',choices=['init','prepare','ingest','assemble','preflight']);a.add_argument('--row',type=int,default=1);a.add_argument('--col',type=int,default=1);a.add_argument('--attempt',default='v01');a.add_argument('--source');a.add_argument('--receipt');a.add_argument('--request');a.add_argument('--content-prefix-file');a.add_argument('--anchor-top');a.add_argument('--anchor-left');a.add_argument('--content-prefix',default='');args=a.parse_args()
rr,cc=n.tile_numbers(args.tile)
assert 9<=rr<=16 and 7<=cc<=8
class Owned(n.Pipeline):
 def current_refs(self):
  return super().current_refs()+[self.ref(SW/'pipeline-tools/local-continuation-audit-20261011/r12-firstrow/ref-stone-context.png','style-only approved calm natural stone surface; do not copy its grout layout or objects')]
p=Owned(args.tile)
if args.action=='init':r=p.init()
elif args.action=='prepare':
 args.content_prefix+='\nImage 5 is ONLY a clean natural stone surface finish reference. Match its quiet softly varied painted limestone, but never transfer its geometry, grout layout or red paper. No repeating weave, scallops, cellular texture, pebble noise, or dense microtexture. Preserve all image-1 ground ornaments exactly where present, without creating complete new emblems.\n'
 r=p.prepare(args)
elif args.action=='ingest':r=p.ingest(args)
else:r=p.assemble(args.action=='preflight',2)
print(json.dumps(r,ensure_ascii=False))
