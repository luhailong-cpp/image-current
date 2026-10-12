from pathlib import Path
import json,sys,runpy
root=Path(__file__).resolve().parent.parent
j=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
sys.argv=[str(root/"ingest.py"),j["raw"],j["output"],j["prompt"],j["receipt"],json.dumps(j["references"],ensure_ascii=False)]
runpy.run_path(str(root/"ingest.py"),run_name="__main__")

