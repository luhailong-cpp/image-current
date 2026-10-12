"""Verify current handoff evidence and original assets after a hydrated clone.

Usage: python docs/migration-current-20261012/verify_portable_evidence.py
Only reads repository files. No Git, network, changes or original-machine paths.
"""
from pathlib import Path
import argparse,hashlib,json,sys

def digest(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def rows(path):
 with path.open(encoding='utf-8') as f:
  for line in f:
   if line.strip():yield json.loads(line)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path)
 a=p.parse_args();package=Path(__file__).resolve().parent;root=(a.repository or package.parent.parent).resolve()
 errors=[];cache={};count=0
 def check(relative,expected,size=None):
  nonlocal count
  path=(root/relative).resolve()
  if root not in path.parents:errors.append({'path':relative,'error':'outside repository'});return
  if not path.is_file():errors.append({'path':relative,'error':'missing (hydrate Git LFS objects first)'});return
  if size is not None and path.stat().st_size!=size:errors.append({'path':relative,'error':'size differs'});return
  actual=cache.setdefault(str(path),None)
  if actual is None:actual=digest(path);cache[str(path)]=actual
  if actual!=expected:errors.append({'path':relative,'error':'SHA256 differs'})
  count+=1
 inventory=json.loads((package/'package-files-sha256.json').read_text('utf-8'))
 for r in inventory['entries']:check((package/r['package_path']).relative_to(root).as_posix(),r['sha256'],r['size'])
 for r in rows(package/'source-to-portable-mapping.jsonl'):check(r['portable_repository_path'],r['sha256'],r['bytes'])
 protected=list(rows(package/'protected-originals-6516.jsonl'))
 absent=list(rows(package/'authorized-absent-screenshots-186.jsonl'))
 if len(protected)!=6516 or len(absent)!=186:errors.append({'error':'protection roster counts differ'})
 for r in protected:check(r['path'],r['sha256'],r['size'])
 for r in absent:
  if (root/r['path']).exists():errors.append({'path':r['path'],'error':'authorized absent screenshot reappeared'})
 print(json.dumps({'passed':not errors,'checked_records':count,'unique_files_hashed':len(cache),
                   'protected_originals':len(protected),'authorized_absences':len(absent),'errors':errors},indent=2))
 return 1 if errors else 0
if __name__=='__main__':sys.exit(main())
