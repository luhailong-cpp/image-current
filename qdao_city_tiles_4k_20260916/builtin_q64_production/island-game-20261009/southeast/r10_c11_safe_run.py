"""Tile-only atomic progress writes; no shared workflow mutation."""
import json, os, runpy, sys, uuid
import workflow
old_write=workflow.write
def write(p,value):
    if p==workflow.PROGRESS_FILE:
        tmp=p.parent/('r10_c11-progress-'+uuid.uuid4().hex+'.tmp')
        old_write(tmp,value)
        os.replace(tmp,p)
    else:
        old_write(p,value)
workflow.write=write
mode=sys.argv.pop(1)
if mode=='ingest':
    workflow.ingest(*sys.argv[1:5])
elif mode=='progress':
    workflow.progress(**json.loads(sys.argv[1]))
else:
    sys.argv[0]=str(workflow.ROOT/mode)
    runpy.run_path(sys.argv[0],run_name='__main__')
