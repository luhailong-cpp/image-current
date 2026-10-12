from pathlib import Path
import ast,json
R=Path(__file__).resolve().parents[1]
tree=ast.parse((R/"tools/build_run_preview.py").read_text(encoding="utf-8"))
vals={}
for st in tree.body:
 if isinstance(st,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ["HTML","HELPER"] for t in st.targets):
  vals[st.targets[0].id]=ast.literal_eval(st.value)
groups=[]
for d in ["N","NE","E","SE","S","SW","W","NW"]:
 p=R/f"grounding4/{d}/selected.json"
 if not p.exists():continue
 rows=json.loads(p.read_text(encoding="utf-8-sig"))
 groups.append({"direction":d,"frames":[{"frame":r["frame"],"url":"../"+r["exportFile"],"source":r["exportFile"],"exists":True} for r in rows],"contactSegments":[{"supportFoot":rows[0]["supportFoot"],"frames":list(range(1,9))},{"supportFoot":rows[8]["supportFoot"],"frames":list(range(9,17))}],"groundingReviewed":False})
html=vals["HTML"].replace("__DATA__",json.dumps(groups,ensure_ascii=False)).replace("__HELPER__",vals["HELPER"]).replace("20 星阵少女 · 八方向跑步","20 星阵少女 · 当前选帧复核").replace("/128 已载入","/"+str(len(groups)*16)+" 已载入")
(R/"preview/grounding-pairs-review.html").write_text(html,encoding="utf-8")
print(len(groups),len(groups)*16)

