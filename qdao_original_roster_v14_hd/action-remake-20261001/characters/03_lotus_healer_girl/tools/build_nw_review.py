"""Refresh private N/NW review from explicit current selections, never filename phases."""
from pathlib import Path
from PIL import Image, ImageDraw
import argparse, hashlib, json
B = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument("--direction", choices=["N", "NW"], default="NW")
direction = parser.parse_args().direction
input_path = B / "review" / f"run-{direction}-sequence-input.json"
data = json.loads(input_path.read_text(encoding="utf-8-sig"))
frames = sorted(data["frames"], key=lambda frame: frame["slot"])
if [frame["slot"] for frame in frames] != list(range(1, 17)):
    raise ValueError("Exactly16 explicit selected slots required.")
frame_ms = 75
data["timing"] = {"frameMs":frame_ms,"trialCycleMs":16*frame_ms,"defaultPreviewCycleMs":16*frame_ms,
 "selectedProductionCycleMs":None,"phaseWeightsApplied":False,"uniformComparisonMs":[16*frame_ms],
 "trialMeaning":"Latest explicit user instruction: uniform75ms/frame,1200ms/cycle; client unconfirmed."}
contact = Image.new("RGB",(1280,1380),(35,41,48))
draw = ImageDraw.Draw(contact)
seen = set()
for index,frame in enumerate(frames):
    source = B/frame["source"]
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != frame["sourceSha256"] or digest in seen:
        raise ValueError(f"Changed or duplicate selected source: {source}")
    seen.add(digest)
    frame["durationMs"] = frame_ms
    picture = Image.open(source).convert("RGBA").resize((320,320),Image.Resampling.LANCZOS)
    x,y = index%4*320,index//4*345
    contact.paste(picture,(x,y+25),picture)
    draw.text((x+8,y+5),f"{direction}{index+1:02} | {source.stem} |75ms",fill="white")
for event in data.get("events",[]):
    slot = int(event.get("frame",event.get("slot")))
    if not 1 <= slot <= 16:
        raise ValueError("Event frame outside selected cycle.")
    start = sum(frame["durationMs"] for frame in frames if frame["slot"] < slot)
    event.update(frame=slot,slot=slot,timeMs=start,startMs=start)
data["frames"] = frames
data["visualAccepted"] = False
data["status"] = "candidate_not_accepted"
input_path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
contact.save(B/"review"/f"run-{direction}-contact.png")
print(json.dumps({"direction":direction,"selected":len(frames),"uniqueSHA":len(seen),"cycleMs":sum(frame["durationMs"] for frame in frames),"eventsMs":[event["timeMs"] for event in data.get("events",[])]}))

