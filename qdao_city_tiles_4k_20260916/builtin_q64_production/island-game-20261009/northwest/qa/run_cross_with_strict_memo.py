"""Invocation-local strict validation memo. Original validators run for first visit.
Every cache hit rehashes every observed transitive input, including missing
historical reference state; no persisted cache or proof substitution.
"""
from pathlib import Path
import sys,hashlib,copy,collections,json
Z=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Z))
import apply_native_tile_repair as r
import historical_reference as h
import cross_tile_native_repair as cross
import assemble_connected_tiles as connected
orig_reconstruct=connected.reconstruct_padded
orig_validate,orig_info,orig_read=r.validate_base,r.file_info,r.read_json
orig_hist,orig_reference=h.file_record,h.reference
stack=[]; cache=collections.OrderedDict()
stats=dict(hits=0,misses=0,rehashes=0,dependencyChanges=0)
def digest(p):
 p=Path(p).resolve()
 return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
def note(path,value):
 for frame in stack:frame["deps"][str(Path(path).resolve())]=value
def info(p):
 result=orig_info(p);note(p,result["sha256"]);return result
def read(p):
 info(p);return orig_read(p)
def hist(p):
 result=orig_hist(p);note(p,result["sha256"]);return result
def reference(value,base,generation=None):
 p=Path(value["path"]);p=(p if p.is_absolute() else base/p).resolve()
 note(p,digest(p))
 return orig_reference(value,base,generation)
def memo_call(image,record,seen=None,kind="base"):
 image,record=Path(image).resolve(),Path(record).resolve()
 seen=set() if seen is None else set(seen)
 r.require(record not in seen and len(seen)<32,"Cyclic or excessive cached provenance chain.")
 depth=len(seen)
 for frame in stack:frame["maxDepth"]=max(frame["maxDepth"],depth)
 key=(kind,str(image),str(record));hit=cache.get(key)
 if hit and not seen.intersection(Path(p) for p in hit["deps"]) and depth+hit["extraDepth"]<32:
  unchanged=True
  for path,expected in hit["deps"].items():
   stats["rehashes"]+=1
   if digest(path)!=expected:unchanged=False;break
  if unchanged:
   stats["hits"]+=1;cache.move_to_end(key)
   for path,value in hit["deps"].items():note(path,value)
   for frame in stack:frame["maxDepth"]=max(frame["maxDepth"],depth+hit["extraDepth"])
   return hit["pixels"].copy(),copy.deepcopy(hit["proof"])
  stats["dependencyChanges"]+=1
 stats["misses"]+=1
 frame=dict(deps={},maxDepth=depth);stack.append(frame)
 try:
  pixels,proof=(orig_validate if kind=="base" else orig_reconstruct)(image,record,seen)
 finally:stack.pop()
 entry=dict(pixels=pixels.copy(),proof=copy.deepcopy(proof),deps=frame["deps"],extraDepth=frame["maxDepth"]-depth)
 cache[key]=entry;cache.move_to_end(key)
 while len(cache)>32:cache.popitem(last=False)
 return pixels,proof
def validate(image,record,seen=None):
 return memo_call(image,record,seen,"base")
def reconstruct(image,record,seen=None):
 return memo_call(image,record,seen,"padded")
r.file_info=info;r.read_json=read;r.validate_base=validate
connected.reconstruct_padded=reconstruct
h.file_record=hist;h.reference=reference
if __name__=="__main__":
 if sys.argv[1:]==["--server"]:
  print(json.dumps({"status":"strict_memo_server_ready"}),flush=True)
  for line in sys.stdin:
   request=json.loads(line)
   if request.get("exit"):break
   sys.argv=[__file__]+request["argv"]
   try:cross.main()
   except Exception as error:print(json.dumps({"status":"failed","error":str(error)}),flush=True)
   print(json.dumps({"requestComplete":True,"strictInvocationMemo":stats}),flush=True)
 else:
  try:cross.main()
  finally:print(json.dumps({"strictInvocationMemo":stats}),file=sys.stderr)

