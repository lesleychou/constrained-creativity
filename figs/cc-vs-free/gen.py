import json
TEAL, PALE, INK, MUTED, GREY, BFILL, BSTROKE, RED, LLMF = "#117788","#c5e5e5","#262626","#4e4e4e","#868686","#f2f2f2","#8c8c8c","#c00000","#e7e7e7"
W, H = 504, 246
CL, CR, GX = 112, 392, 252
out = []
def rect(x,y,w,h,fill,stroke,sw=0.72): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="1.5" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def text(x,y,s,size=7,anchor="middle",fill=INK,weight=None,italic=False):
    a = f' font-weight="bold"' if weight else ''
    a += ' font-style="italic"' if italic else ''
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{a}>{s}</text>'
nodes, edges, svg_panels = [], [], {"p-free": [], "p-cc": []}
def node(pid, nid, label, x,y,w,h, fill, stroke, role, sub=None, tfill=INK, extra="", parent_panel=True, kind="module"):
    nodes.append(dict(id=nid,label=label,sublabel=sub,kind=kind,role=role,panel=pid))
    cx = x+w/2
    if sub:
        t = text(cx, y+h/2-1.2, label, 7, fill=tfill) + text(cx, y+h/2+6.6, sub, 6, fill=MUTED)
    else:
        t = text(cx, y+h/2+2.5, label, 7, fill=tfill)
    svg_panels[pid].append(f'<g id="n:{nid}" data-kind="node" data-role="{role}" data-panel="{pid}">{rect(x,y,w,h,fill,stroke)}{extra}{t}</g>')
def edge(pid, eid, frm, to, d, color, sw, kind="data", dash=None, label=None, lx=0, ly=0, lanchor="start", lcolor=MUTED, marker="g"):
    e = dict(id=eid, **{"from": frm}, to=to, kind=kind)
    if dash: e["style"]="dashed"
    if label: e["label"]=label
    edges.append(e)
    da = f' stroke-dasharray="2.5 1.9"' if dash else ''
    lab = text(lx, ly, label, 6, lanchor, lcolor) if label else ''
    svg_panels[pid].insert(0, f'<g id="e:{eid}" data-kind="edge" data-from="{frm}" data-to="{to}" data-edge-kind="{kind}"><path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{da} marker-end="url(#ah-{marker})"/>{lab}</g>')

# ---- left: unconstrained
P="p-free"
node(P,"free-input","Task + all raw data",CL-38,22,76,24,"#ffffff",INK,"existing",sub="in the prompt")
node(P,"free-llm","LLM",CL-38,58,76,16,LLMF,INK,"existing")
node(P,"free-code","Arbitrary code",CL-38,86,76,22,BFILL,BSTROKE,"baseline",sub="any code, any action")
node(P,"free-out","Unchecked answer",CL-38,176,76,16,BFILL,BSTROKE,"baseline")
edge(P,"e-free-1","free-input","free-llm",f"M{CL} 46 V58",GREY,0.72)
edge(P,"e-free-2","free-llm","free-code",f"M{CL} 74 V86",GREY,0.72)
edge(P,"e-free-3","free-code","free-out",f"M{CL} 108 V176",GREY,0.72,label="no verification",lx=CL+4,ly=144.5)
# ---- right: constrained creativity
P="p-cc"
node(P,"cc-task","Task",340,22,40,24,"#ffffff",INK,"existing")
node(P,"cc-dsl","DSL",392,22,64,24,PALE,TEAL,"novel",sub="operators + structure")
node(P,"cc-llm","LLM",CR-38,58,76,16,LLMF,INK,"existing")
dag = (f'<g data-symbol="dag" fill="{TEAL}" stroke="{TEAL}" stroke-width="0.5">'
       '<path d="M409 97 L417 92.5 M409 97 L417 101.5 M422 92.5 L428 97 M422 101.5 L428 97" fill="none"/>'
       '<rect x="404" y="94.5" width="5" height="5"/><rect x="417" y="90" width="5" height="5"/>'
       '<rect x="417" y="99" width="5" height="5"/><rect x="428" y="94.5" width="5" height="5"/></g>')
nodes.append(dict(id="cc-prog",label="DSL program",kind="module",role="novel",panel=P))
svg_panels[P].append(f'<g id="n:cc-prog" data-kind="node" data-role="novel" data-panel="{P}">{rect(CR-46,86,92,22,PALE,TEAL)}{dag}{text(CR-40,99.5,"DSL program",7,"start")}</g>')
node(P,"cc-verify","Verifier",CR-24,120,48,16,PALE,TEAL,"novel")
node(P,"cc-runtime","Runtime engine",CR-32,148,64,16,PALE,TEAL,"novel")
node(P,"cc-data","Data",448,148,30,16,"#ffffff",INK,"existing")
node(P,"cc-out","Verified answer",CR-38,176,76,16,TEAL,TEAL,"novel",tfill="#ffffff")
edge(P,"e-cc-1","cc-task","cc-llm","M360 46 V58",TEAL,1.0,marker="t")
edge(P,"e-cc-2","cc-dsl","cc-llm","M424 46 V58",TEAL,1.0,marker="t")
edge(P,"e-cc-3","cc-llm","cc-prog",f"M{CR} 74 V86",TEAL,1.0,marker="t")
edge(P,"e-cc-4","cc-prog","cc-verify",f"M{CR} 108 V120",TEAL,1.0,marker="t")
edge(P,"e-cc-5","cc-verify","cc-runtime",f"M{CR} 136 V148",TEAL,1.0,marker="t",label="valid",lx=CR+4,ly=144.2)
edge(P,"e-cc-6","cc-runtime","cc-out",f"M{CR} 164 V176",TEAL,1.0,marker="t")
edge(P,"e-cc-7","cc-data","cc-runtime","M448 156 H424",GREY,0.72)
edge(P,"e-cc-retry","cc-verify","cc-llm","M416 128 H452 V66 H430",TEAL,0.72,kind="feedback",dash=True,marker="t",
     label="retry if invalid",lx=456,ly=99.5,lcolor=TEAL)
# ---- gutter + scorecard
ann = []
def check(x,y): return f'<path d="M{x} {y-2.6} l1.9 2.1 l3.6 -4.6" fill="none" stroke="{TEAL}" stroke-width="1"/>'
def cross(x,y): return f'<path d="M{x} {y-4.6} l4.2 4.2 M{x+4.2} {y-4.6} l-4.2 4.2" fill="none" stroke="{RED}" stroke-width="1"/>'
gut = []
for aid,lab,y in [("lbl-input","Input",36.5),("lbl-output","Output",186.5)]:
    ann.append(dict(id=aid,kind="label",text=lab))
    gut.append(f'<g id="a:{aid}" data-kind="annotation">{text(GX,y,lab,7,fill=MUTED,weight=True)}</g>')
gut.append(f'<g id="a:rule" data-kind="annotation"><path d="M8 202 H496" stroke="#cccccc" stroke-width="0.6"/></g>')
ann.append(dict(id="rule",kind="label",text="scorecard divider"))
widths = {"Hard to verify":41.5,"Verifiable":29.3,"Low":12.9,"High":14.5}
rows = [("Reliability","Hard to verify","Verifiable"),("Accuracy","Low","High"),("Cost","High","Low")]
for i,(cat,lv,rv) in enumerate(rows):
    y = 216+i*12
    k = cat.lower()
    ann.append(dict(id=f"sc-{k}",kind="label",text=cat))
    gut.append(f'<g id="a:sc-{k}" data-kind="annotation">{text(GX,y,cat,7,fill=MUTED,weight=True)}</g>')
    for side,val,c,mark in [("free",lv,CL,cross),("cc",rv,CR,check)]:
        x0 = c-24
        ann.append(dict(id=f"v-{side}-{k}",kind="verdict",text=val))
        gut.append(f'<g id="a:v-{side}-{k}" data-kind="annotation">{mark(x0,y)}{text(x0+8.5,y,val,7,"start")}</g>')
titles = (f'<g id="a:title-free" data-kind="annotation">{text(CL,12,"Unconstrained AI",8,fill=MUTED,weight=True)}</g>'
          f'<g id="a:title-cc" data-kind="annotation">{text(CR,12,"Constrained Creativity",8,fill=TEAL,weight=True)}</g>')
ann += [dict(id="title-free",kind="label",text="Unconstrained AI"),dict(id="title-cc",kind="label",text="Constrained Creativity")]
defs = ('<defs>'
  f'<marker id="ah-g" viewBox="0 0 5 4" refX="5" refY="2" markerWidth="5" markerHeight="4" markerUnits="userSpaceOnUse" orient="auto"><path d="M0 0 L5 2 L0 4 z" fill="{GREY}"/></marker>'
  f'<marker id="ah-t" viewBox="0 0 5 4" refX="5" refY="2" markerWidth="5" markerHeight="4" markerUnits="userSpaceOnUse" orient="auto"><path d="M0 0 L5 2 L0 4 z" fill="{TEAL}"/></marker>'
  '</defs>')
body = "".join(f'<g id="p:{p}" data-kind="panel">{"".join(v)}</g>' for p,v in svg_panels.items())
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}pt" height="{H}pt" '
       f"font-family=\"'TeX Gyre Heros', 'Helvetica Neue', Helvetica, Arimo, Arial, sans-serif\" font-size=\"7\" "
       f'data-spec="cc-vs-free" data-spec-version="1"><rect width="{W}" height="{H}" fill="#ffffff"/>{defs}{body}{titles}{"".join(gut)}</svg>')
open("fig.svg","w").write(svg)
for n in nodes:
    if n.get("sublabel") is None: n.pop("sublabel",None)
spec = {"meta":{"id":"cc-vs-free","title":"Unconstrained AI vs. Constrained Creativity","kind":"mechanism","figure_kind":"mechanism",
  "column":"double","width_pt":W,"max_height_pt":H,"template":"mechanism","direction":"top-down","panels":2,"palette":"cool-grey-cyan",
  "font":"helvetica","step_markers":"none","language":"en","version":1,
  "mechanism":{"group":"comparison","groups":[],"worked_example":False,"base":"flowchart","arrangement":"panels-row","frame_template":"aligned",
    "delta_marking":"colour","zoom_callout":False,"notes":"rows aligned across panels; centre gutter carries Input/Output row labels and the qualitative scorecard; height exceeds the 130-180 pt band deliberately (blog figure with scorecard)"},
  "caption_draft":open("brief.md").read().split("**Caption draft.** ")[1].strip()},
 "panels":[{"id":"p-free","label":"Unconstrained AI","axis":"alternatives","order":0,"differs":"","verdict":"hard to verify, low accuracy, high cost"},
   {"id":"p-cc","label":"Constrained Creativity","axis":"alternatives","order":1,"template_of":"p-free",
    "differs":"LLM composes a DSL program that a verifier checks before a runtime engine executes it over the data","verdict":"verifiable, high accuracy, low cost"}],
 "nodes":nodes,"edges":edges,"annotations":ann}
json.dump(spec,open("spec.json","w"),indent=1)
