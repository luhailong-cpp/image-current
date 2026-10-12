"""Prepare reversible export-coordinate inputs, not synthetic animation frames."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
def prepare(action,direction,index,label=None,archive=False):
    source=ROOT/"runtime"/action/direction/f"{index:02}.png"
    record=ROOT/"records"/f"{action}-{direction}"/f"{index:02}.generation.json"
    old=json.loads(record.read_text(encoding="utf-8-sig"))
    historical=record.with_name(f"{index:02}.pre-guardfix-20261008.generation.json")
    if archive:
        if historical.exists():
            assert json.loads(historical.read_text(encoding="utf-8"))["sha256"]==sha(source), "Do not re-prepare after a repair export"
        else:save(historical,old)
    dest=ROOT/"repair-inputs"/(label or f"{action}-{direction}-{index:02}.png")
    dest.parent.mkdir(exist_ok=True)
    with Image.open(source) as im:
        # Undo only the already-documented whole-canvas export placement. Pixels are
        # resampled from the final export, not claimed to be recovered native pixels.
        im.crop((32,16,992,976)).resize((1254,1254),Image.Resampling.LANCZOS).save(dest)
    save(dest.with_suffix(".input.json"),{
        "file":dest.relative_to(ROOT).as_posix(),"sha256":sha(dest),
        "createdAt":datetime.now(timezone.utc).isoformat(),
        "derivedFrom":{"file":source.relative_to(ROOT).as_posix(),"sha256":sha(source),"record":(historical if archive else record).relative_to(ROOT).as_posix()},
        "operation":{"type":"edit-input-coordinate-normalization","crop":[32,16,992,976],"resize":[1254,1254],"newPoseCreated":False,"nativePixelsRecovered":False},
        "configSnapshot":old["configSnapshot"],"actualModel":old["actualModel"],"actualQuality":old["actualQuality"]})
    return str(dest)
if __name__=="__main__":
    files=[prepare("attack","E",1,archive=True)]
    for action,count in [("hit",6),("attack",12)]:
        files += [prepare(action,"W",i,archive=True) for i in range(1,count+1)]
    files += [prepare("attack","E",12,label="baseline-E.png"),prepare("cast","W",16,label="baseline-W.png")]
    print(json.dumps({"prepared":len(files),"files":files},ensure_ascii=False))
