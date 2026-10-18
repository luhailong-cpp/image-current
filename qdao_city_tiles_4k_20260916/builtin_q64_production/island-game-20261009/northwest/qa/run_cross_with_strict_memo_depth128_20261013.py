"""Versioned long-chain strict runner. Retains cycle, hash and pixel checks.
Only three original provenance depth guards and memo depth reuse guards change
from 32 to 128. Shared production scripts remain unmodified.
"""
from pathlib import Path
import sys,ast,inspect,hashlib,json
Z=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Z))
import apply_native_tile_repair as r
import cross_tile_native_repair as c
import assemble_connected_tiles as a
POLICY=128
changes=[]
class DepthGuard(ast.NodeTransformer):
 def __init__(self):self.count=0
 def visit_Compare(self,node):
  self.generic_visit(node)
  text=ast.unparse(node.left)
  if ('seen' in text or 'extraDepth' in text) and len(node.ops)==1 and isinstance(node.ops[0],ast.Lt) and isinstance(node.comparators[0],ast.Constant) and node.comparators[0].value==32:
   node.comparators[0]=ast.copy_location(ast.Constant(POLICY),node.comparators[0]);self.count+=1
  return node
def patch_function(module,name):
 fn=getattr(module,name);tree=ast.parse(inspect.getsource(fn));changer=DepthGuard();tree=changer.visit(tree);ast.fix_missing_locations(tree)
 assert changer.count==1,(name,changer.count)
 exec(compile(tree,fn.__code__.co_filename,'exec'),module.__dict__)
 changes.append(dict(file=module.__file__,function=name,depthGuardChanges=changer.count))
for module,name in [(r,'validate_base'),(c,'validate_operation'),(a,'validate_projection')]:patch_function(module,name)
# Cycle rejection must still precede any file access.
dummy=Z/'qa/does-not-exist-depth-policy-test.json'
try:r.validate_base(dummy,dummy,{dummy.resolve()})
except Exception as e:assert 'Cyclic' in str(e),str(e)
else:raise AssertionError('Cycle guard disabled')
source=Z/'qa/run_cross_with_strict_memo.py'
tree=ast.parse(source.read_text(encoding='utf-8-sig'));changer=DepthGuard();tree=changer.visit(tree);ast.fix_missing_locations(tree)
assert changer.count==2,changer.count
policy=dict(operation='strict native replay with explicit expanded bounded ancestry',depthLimit=POLICY,oldDepthLimit=32,cycleCheckStillEnabled=True,hashAndPixelChecksUnchanged=True,wrapper=dict(path=Path(__file__).as_posix(),sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),originalScripts=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [Path(r.__file__),Path(c.__file__),Path(a.__file__),source]],changes=changes,memoGuardChanges=changer.count)
print(json.dumps({'depthPolicy':policy}),flush=True)
g=dict(__name__='__main__',__file__=str(source))
exec(compile(tree,str(source),'exec'),g)

