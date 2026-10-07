import json
# Palette: one accent (blog orange) for everything CC adds; greys for the shared skeleton and the baseline.
ACC, PALE, INK, MUTED, GREY, BFILL, BSTROKE, RED, LLMF = "#C2410C","#FDEBDD","#262626","#4e4e4e","#868686","#f2f2f2","#8c8c8c","#c00000","#e7e7e7"
W, H = 504, 196
XL, XR = 52, 304          # left edge of the skeleton column in each panel
SW = 88                   # skeleton box width
SL, SR = 156, 412         # side column left edge in each panel
ROW = dict(task=(26,18), llm=(62,18), out=(98,34), ans=(150,26))
nodes, edges, ann = [], [], []
panels = {"p-free": [], "p-cc": []}

def rect(x,y,w,h,fill,stroke,sw=0.72,dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="1.5" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'
def text(x,y,s,size=7,anchor="middle",fill=INK,bold=False,extra=""):
    b = ' font-weight="bold"' if bold else ''
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{b}{extra}>{s}</text>'
def node(pid,nid,label,x,y,w,h,fill,stroke,role,sub=None,tfill=INK,sfill=MUTED,pict="",label_top=False,dash=None):
    nodes.append({k:v for k,v in dict(id=nid,label=label,sublabel=sub,kind="module",role=role,panel=pid).items() if v is not None})
    cx = x+w/2
    if label_top: t = text(cx, y+10, label, 7, fill=tfill)
    elif sub: t = text(cx, y+h/2-1.2, label, 7, fill=tfill) + text(cx, y+h/2+6.8, sub, 6, fill=sfill)
    else: t = text(cx, y+h/2+2.5, label, 7, fill=tfill)
    panels[pid].append(f'<g id="n:{nid}" data-kind="node" data-role="{role}" data-panel="{pid}">{rect(x,y,w,h,fill,stroke,dash=dash)}{pict}{t}</g>')
def edge(pid,eid,frm,to,d,color,sw=0.72,kind="data",dash=False,marker="g",start=False,label=None,lab_svg=""):
    e = {"id":eid,"from":frm,"to":to,"kind":kind}
    if dash: e["style"]="dashed"
    if label: e["label"]=label
    edges.append(e)
    da = ' stroke-dasharray="2.5 1.9"' if dash else ''
    ms = f' marker-start="url(#as-{marker})"' if start else ''
    panels[pid].insert(0,f'<g id="e:{eid}" data-kind="edge" data-from="{frm}" data-to="{to}" data-edge-kind="{kind}"><path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{da}{ms} marker-end="url(#ah-{marker})"/>{lab_svg}</g>')

def skeleton(pid, x0, pre, col, sw, mk, out_label, out_fill, out_stroke, out_role, pict, ans_sub, ans_fill, ans_stroke, ans_tfill, ans_sfill, ans_role, out_dash=None):
    cx = x0+SW/2
    y,h = ROW["task"]; node(pid,f"{pre}-task","Task",x0+SW/2-24,y,48,h,"#ffffff",INK,"existing")
    y,h = ROW["llm"];  node(pid,f"{pre}-llm","LLM",x0,y,SW,h,LLMF,INK,"existing")
    y,h = ROW["out"];  node(pid,f"{pre}-out",out_label,x0,y,SW,h,out_fill,out_stroke,out_role,pict=pict,label_top=True,dash=out_dash)
    y,h = ROW["ans"];  node(pid,f"{pre}-ans","Answer",x0,y,SW,h,ans_fill,ans_stroke,ans_role,sub=ans_sub,tfill=ans_tfill,sfill=ans_sfill)
    t,l,o,a = ROW["task"],ROW["llm"],ROW["out"],ROW["ans"]
    edge(pid,f"e-{pre}-1",f"{pre}-task",f"{pre}-llm",f"M{cx} {t[0]+t[1]} V{l[0]}",col,sw,marker=mk)
    edge(pid,f"e-{pre}-2",f"{pre}-llm",f"{pre}-out",f"M{cx} {l[0]+l[1]} V{o[0]}",col,sw,marker=mk)
    edge(pid,f"e-{pre}-3",f"{pre}-out",f"{pre}-ans",f"M{cx} {o[0]+o[1]} V{a[0]}",col,sw,marker=mk)
    # iterate loop: output -> back to LLM, on the left of the skeleton, same in both panels
    ly, oy = l[0]+l[1]/2, o[0]+o[1]/2
    lx = x0-16
    lab = text(lx-3.5, (ly+oy)/2, "iterate", 6, fill=col if col!=GREY else MUTED, extra=f' transform="rotate(-90 {lx-3.5} {(ly+oy)/2})"')
    edge(pid,f"e-{pre}-iter",f"{pre}-out",f"{pre}-llm",f"M{x0} {oy} H{lx} V{ly} H{x0}",col,0.72,kind="feedback",dash=True,marker=mk,label="iterate",lab_svg=lab)

# ---- left: free-form LLM. Arbitrary fragments: different sizes, slightly rotated, scattered.
frag = (f'<g data-symbol="fragments" fill="#ffffff" stroke="{BSTROKE}" stroke-width="0.6">'
  '<g transform="rotate(-9 66 119)"><rect x="59" y="113" width="15" height="11" rx="1"/><path d="M61.5 116.5 h8 M61.5 119 h10 M61.5 121.5 h6" fill="none"/></g>'
  '<g transform="rotate(7 87 115)"><rect x="79" y="111" width="17" height="8" rx="1"/><path d="M81.5 115 h11" fill="none"/></g>'
  '<g transform="rotate(-4 108 122)"><path d="M98 118 h20 M98 121.5 h14 M98 125 h18" fill="none"/></g>'
  '<g transform="rotate(10 128 116)"><rect x="123" y="110" width="10" height="13" rx="1"/><path d="M125.5 113.5 h5 M125.5 116.5 h4 M125.5 119.5 h5" fill="none"/></g>'
  f'<path d="M66 128.5 h12" fill="none"/></g>')
skeleton("p-free",XL,"free",GREY,0.72,"g","Arbitrary programs / text",BFILL,BSTROKE,"baseline",frag,
         "no evidence",BFILL,BSTROKE,INK,MUTED,"baseline")

# ---- right: constrained creativity. Neat DAG of building blocks.
c = XR+SW/2; y0 = 120
dag = (f'<g data-symbol="dag" fill="{ACC}" stroke="{ACC}" stroke-width="0.6">'
  f'<path d="M{c-18} {y0} L{c-7} {y0-5} M{c-18} {y0} L{c-7} {y0+5} M{c-2} {y0-5} L{c+9} {y0} M{c-2} {y0+5} L{c+9} {y0} M{c+14} {y0} H{c+20}" fill="none"/>'
  f'<rect x="{c-23}" y="{y0-2.5}" width="5" height="5"/><rect x="{c-7}" y="{y0-7.5}" width="5" height="5"/>'
  f'<rect x="{c-7}" y="{y0+2.5}" width="5" height="5"/><rect x="{c+9}" y="{y0-2.5}" width="5" height="5"/>'
  f'<rect x="{c+20}" y="{y0-2.5}" width="5" height="5"/></g>')
skeleton("p-cc",XR,"cc",ACC,1.0,"a","DSL program",PALE,ACC,"novel",dag,
         "explained, with evidence",ACC,ACC,"#ffffff","#ffffff","novel")
P="p-cc"
y,h = ROW["task"]; node(P,"cc-dsl","DSL / Playbook",SR,y,80,h,PALE,ACC,"novel")
o = ROW["out"]; ry = o[0]+o[1]/2
node(P,"cc-runtime","DSL runtime engine",SR,ry-9,80,18,PALE,ACC,"novel")
l = ROW["llm"]
edge(P,"e-cc-dsl","cc-dsl","cc-llm",f"M{SR+40} {y+h} V{l[0]+l[1]/2} H{XR+SW}",ACC,1.0,marker="a")
edge(P,"e-cc-run","cc-out","cc-runtime",f"M{XR+SW} {ry} H{SR}",ACC,1.0,marker="a",start=True,label="executes")

# ---- verdicts beside each answer
def check(x,y,col): return f'<path d="M{x} {y-2.6} l1.9 2.1 l3.6 -4.6" fill="none" stroke="{col}" stroke-width="1"/>'
def cross(x,y): return f'<path d="M{x+0.4} {y-4.6} l4 4 M{x+4.4} {y-4.6} l-4 4" fill="none" stroke="{RED}" stroke-width="1"/>'
qual = ["Expressive","Explainable","Effective","Efficient"]
ay = ROW["ans"][0]+ROW["ans"][1]/2
ys = [ay-13.5+i*9.6 for i in range(4)]
ys = [round(v+2.5,1) for v in ys]
extra = []
for side,x0,marks in [("free",SL,[("ok",GREY)]+[("no",None)]*3),("cc",SR,[("ok",ACC)]*4)]:
    for q,y,(m,col) in zip(qual,ys,marks):
        k=f"v-{side}-{q.lower()}"
        ann.append(dict(id=k,kind="verdict",text=("✓ " if m=="ok" else "✗ ")+q))
        mark = check(x0,y,col) if m=="ok" else cross(x0,y)
        tf = INK if m=="ok" else MUTED
        extra.append(f'<g id="a:{k}" data-kind="annotation">{mark}{text(x0+9,y,q,7,"start",tf)}</g>')
# titles + divider
for aid,lab,x,col in [("title-free","Free-form LLM",XL+SW/2,MUTED),("title-cc","Constrained Creativity",XR+SW/2,ACC)]:
    ann.append(dict(id=aid,kind="label",text=lab))
    extra.append(f'<g id="a:{aid}" data-kind="annotation">{text(x,13,lab,8,fill=col,bold=True)}</g>')
ann.append(dict(id="divider",kind="label",text="panel divider"))
extra.append(f'<g id="a:divider" data-kind="annotation"><path d="M252 6 V{H-6}" stroke="#cccccc" stroke-width="0.6"/></g>')

def mk(i,col):
    return (f'<marker id="ah-{i}" viewBox="0 0 5 4" refX="5" refY="2" markerWidth="5" markerHeight="4" markerUnits="userSpaceOnUse" orient="auto"><path d="M0 0 L5 2 L0 4 z" fill="{col}"/></marker>'
            f'<marker id="as-{i}" viewBox="0 0 5 4" refX="0" refY="2" markerWidth="5" markerHeight="4" markerUnits="userSpaceOnUse" orient="auto"><path d="M5 0 L0 2 L5 4 z" fill="{col}"/></marker>')
defs = f'<defs>{mk("g",GREY)}{mk("a",ACC)}</defs>'
body = "".join(f'<g id="p:{p}" data-kind="panel">{"".join(v)}</g>' for p,v in panels.items())
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}pt" height="{H}pt" '
       f"font-family=\"'TeX Gyre Heros', 'Helvetica Neue', Helvetica, Arimo, Arial, sans-serif\" font-size=\"7\" "
       f'data-spec="freeform-vs-cc" data-spec-version="1"><rect width="{W}" height="{H}" fill="#ffffff"/>{defs}{body}{"".join(extra)}</svg>')
open("fig.svg","w").write(svg)
cap = open("brief.md").read().split("**Caption draft.** ")[1].strip()
spec = {"meta":{"id":"freeform-vs-cc","title":"Free-form LLM vs. Constrained Creativity","kind":"mechanism","figure_kind":"mechanism",
  "column":"double","width_pt":W,"max_height_pt":H,"template":"mechanism","direction":"top-down","panels":2,"palette":"custom",
  "font":"helvetica","step_markers":"none","language":"en","version":1,
  "mechanism":{"group":"comparison","groups":[],"worked_example":False,"base":"flowchart","arrangement":"panels-row","frame_template":"aligned",
    "delta_marking":"colour","zoom_callout":False,"notes":"same four-row skeleton and iterate loop in both panels at identical positions; CC additions (DSL/Playbook, DSL runtime) sit in a side column; verdicts beside each answer"},
  "caption_draft":cap},
 "panels":[{"id":"p-free","label":"Free-form LLM","axis":"alternatives","order":0,"differs":"","verdict":"expressive; not explainable, effective or efficient"},
   {"id":"p-cc","label":"Constrained Creativity","axis":"alternatives","order":1,"template_of":"p-free",
    "differs":"DSL/Playbook constrains the LLM to emit DSL programs run by a DSL runtime engine","verdict":"expressive, explainable, effective, efficient"}],
 "style_overrides":{"palette_roles":{"module":LLMF,"stroke":INK,"text":INK,"accent":ACC,"x-accent_fill":PALE}},
 "nodes":nodes,"edges":edges,"annotations":ann}
json.dump(spec,open("spec.json","w"),indent=1)
