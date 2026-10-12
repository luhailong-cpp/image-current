import json,sys,hashlib
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[1]
action,direction,num=sys.argv[1:4]
ident=f"{action}-{direction}-{int(num):02d}"
receipt=root/"receipts"/(ident+".json")
r=json.loads(receipt.read_text(encoding="utf-8"))
src=Path(r["sourcePath"])
out=root/"runtime"/action/direction/(f"{int(num):02d}.png")
out.parent.mkdir(parents=True,exist_ok=True)
im=Image.open(src); native_size=im.size; native_mode=im.mode
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
native_sha=sha(src)
im.convert("RGBA").resize((1024,1024),Image.Resampling.LANCZOS).save(out)
refs=[dict(path=p,role=role,sha256=sha(Path(p))) for p,role in r["references"]]
record=dict(schemaVersion=1,file=out.relative_to(root).as_posix(),sha256=sha(out),generatedAt=r["completedAt"],width=1024,height=1024,format="PNG",mode="RGBA",tool="image_gen.imagegen",route="builtin",configSnapshot=json.loads(Path("D:/work/image/config/image-generation.json").read_text(encoding="utf-8")),submittedParameters=dict(model=None,quality=None,transparent_background=True,referenced_image_paths=[x["path"] for x in refs]),actualModel=None,actualQuality=None,unverifiedReason="宿主管理，工具没有 model/quality 选择器，返回 image_url/output_hint 未披露实际型号或质量",evidence=dict(receipt=receipt.relative_to(root).as_posix(),fields=["output_hint"],toolResultKeys=["image_url","output_hint"]),prompt="prompts/"+ident+".txt",references=refs,derivedFrom=dict(path=str(src),sha256=native_sha,width=native_size[0],height=native_size[1],mode=native_mode,retention="host-source-until-final-validation"),operation=dict(type="uniform-full-canvas-resize",fromSize=list(native_size),toSize=[1024,1024],filter="LANCZOS",translation=[0,0],perFrameAlignment=False),visualReview=dict(status="individual-pose-reviewed",notes=r.get("visualNotes"),sequence="pending"))
Path(str(out)+".generation.json").write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(dict(file=str(out),size=im.size,sha256=record["sha256"],alpha=Image.open(out).getchannel("A").getextrema())))

