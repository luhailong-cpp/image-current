from pathlib import Path
from types import SimpleNamespace
import json,sys
B=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(B))
from native_pipeline import Pipeline,pid,read
class IndependentPipeline(Pipeline):
 def neighbor(self,row,col,side):
  if (row,col,side) in [(2,2,'left'),(3,1,'top')]:
   selected=self.selected_record(self.tile,2,1,optional=True)
   if selected is None:
    deferred=B/self.tile/'pipeline/p02_01.restart-deferred-repair.json'
    evidence=read(deferred)
    assert evidence['selected'] is False and evidence['status']=='failed_deferred_after_two_repairs'
    digest=self.check(deferred)
    self.warn('same_tile_neighbor_deferred_unselected',sourceTile=self.tile,patch='p02_01',side=side,deferredRecord=str(deferred),deferredSha256=digest,note='Original layout guide retained in absent overlap; pending future real native seam repair, no fake native anchor.')
    return None
  return super().neighbor(row,col,side)
row,col,attempt=sys.argv[1:]
assert (int(row),int(col)) in [(2,2),(3,1)]
args=SimpleNamespace(row=int(row),col=int(col),attempt=attempt,content_prefix=None,content_prefix_file=None,anchor_left=None,anchor_top=None)
print(json.dumps(IndependentPipeline('r15_c05').prepare(args),ensure_ascii=False,indent=2))
