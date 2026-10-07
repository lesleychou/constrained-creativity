import json
# Same skeleton as the right panel of figs/freeform-vs-cc: Task -> LLM -> DSL program -> Answer, DSL/Playbook feeding
# the LLM, DSL runtime engine beside the program, iterate loop on the left. Every box keeps its CC role as title and
# carries LegoRCA's instance underneath (NSDI'27 #768, §3-4, App. C, Fig. 10).
ACC, PALE, INK, MUTED, LLMF = "#C2410C", "#FDEBDD", "#262626", "#5a5a5a", "#e7e7e7"
W, H = 504, 250
X0, SW = 118, 196            # main column
SR, SWS = 346, 150           # side column
CX = X0 + SW / 2
ROW = dict(task=(22, 34), llm=(72, 32), out=(122, 66), ans=(208, 34))
nodes, edges, ann, body, back = [], [], [], [], []

def rect(x, y, w, h, fill, stroke, sw=0.72, rx=1.5):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def text(x, y, s, size=6, anchor="middle", fill=INK, bold=False, extra=""):
    b = ' font-weight="bold"' if bold else ''
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{b}{extra}>{s}</text>'

def node(nid, title, lines, x, y, w, h, fill, stroke, tfill=INK, lfill=MUTED, pict="", role="novel"):
    nodes.append(dict(id=nid, label=title, sublabel=" / ".join(lines) if lines else None, kind="module", role=role))
    nodes[-1] = {k: v for k, v in nodes[-1].items() if v is not None}
    cx = x + w / 2
    t = text(cx, y + 10.5, title, 7, fill=tfill, bold=True)
    for i, s in enumerate(lines):
        t += text(cx, y + 19.5 + i * 7.6, s, 6, fill=lfill)
    body.append(f'<g id="n:{nid}" data-kind="node" data-role="{role}">{rect(x, y, w, h, fill, stroke)}{pict}{t}</g>')

def edge(eid, frm, to, d, kind="data", dash=False, start=False, label=None, lab_svg="", sw=1.0):
    e = {"id": eid, "from": frm, "to": to, "kind": kind}
    if dash: e["style"] = "dashed"
    if label: e["label"] = label
    edges.append(e)
    da = ' stroke-dasharray="2.5 1.9"' if dash else ''
    ms = ' marker-start="url(#as)"' if start else ''
    back.append(f'<g id="e:{eid}" data-kind="edge" data-from="{frm}" data-to="{to}" data-edge-kind="{kind}">'
                f'<path d="M{d}" fill="none" stroke="{ACC}" stroke-width="{sw}"{da}{ms} marker-end="url(#ah)"/>{lab_svg}</g>')

def badge(x, y, n, fill=ACC):
    return (f'<circle cx="{x}" cy="{y}" r="3.8" fill="{fill}"/>'
            + text(x, y + 2.15, str(n), 6, fill="#ffffff", bold=True))

# ---- the skeleton
y, h = ROW["task"]
node("task", "Task", ["KPI alert + baseline / anomalous windows (+ analyst hint)",
                      "e.g. shipping-service avg latency ↑, 14:00–14:30"], X0, y, SW, h, "#ffffff", INK, role="existing")
y, h = ROW["llm"]
node("llm", "LLM", ["Gemini-3.1-Pro: reads operator signatures + schema,", "never the telemetry itself"],
     X0, y, SW, h, LLMF, INK, role="existing")

# DSL program: a miniature of the Fig. 10 DAG, real operator names
y, h = ROW["out"]
dag, dy = [], y + 33          # DAG centre line
ph = 10
cols = [[("aggregate", 33)], [("candidates", 35)],
        [("entity_rca", 46), ("stattest_rca", 46), ("flow_attribution", 46)], [("ranked_leads", 42)]]
inner = SW - 12
gap = (inner - sum(c[0][1] for c in cols)) / (len(cols) - 1)
xs, cur = [], X0 + 6
for c in cols:
    xs.append(cur); cur += c[0][1] + gap
pos = []
for (c, x) in zip(cols, xs):
    ys = [dy] if len(c) == 1 else [dy - 12, dy, dy + 12]
    pos.append([(x, yy, w) for (_, w), yy in zip(c, ys)])
lines = []
for a, b in zip(pos, pos[1:]):
    for (x1, y1, w1) in a:
        for (x2, y2, _) in b:
            lines.append(f'M{x1 + w1} {y1} L{x2} {y2}')
dag.append(f'<path d="{" ".join(lines)}" fill="none" stroke="{ACC}" stroke-width="0.6"/>')
for c, ps in zip(cols, pos):
    for (lab, _), (x, yy, w) in zip(c, ps):
        dag.append(rect(x, yy - ph / 2, w, ph, "#ffffff", ACC, 0.6, 1) + text(x + w / 2, yy + 2.1, lab, 6, fill=ACC))
dag.append(text(CX, y + h - 4.5, "15-operator JSON DAG generated for one Market-CB1 incident", 6, fill=MUTED))
node("program", "DSL program", [], X0, y, SW, h, PALE, ACC, pict=f'<g data-symbol="dag">{"".join(dag)}</g>')

y, h = ROW["ans"]
node("answer", "Answer", ["ranked leads, each with score + evidence",
                          "#1  frontend-1: container network latency"], X0, y, SW, h, ACC, ACC, "#ffffff", "#ffffff")

# ---- side column
ty, th = ROW["task"]
node("dsl", "DSL / Playbook", ["grammar: typed, loop-free DAG → one answer",
                               "19 operators: 7 generate · 10 score · 2 summarize",
                               "11 playbooks, specialised per deployment"], SR, ty, SWS, 46, PALE, ACC)
o = ROW["out"]; ry = o[0] + 33
node("runtime", "DSL runtime engine", ["verifier: operators exist · types match · acyclic",
                                      "Ray executor: parallel SQL / ML ops, cached, local"], SR, ry - 17, SWS, 34, PALE, ACC)

# ---- edges
t, l, a = ROW["task"], ROW["llm"], ROW["ans"]
edge("e-1", "task", "llm", f"{CX} {t[0] + t[1]} V{l[0]}")
edge("e-2", "llm", "program", f"{CX} {l[0] + l[1]} V{o[0]}")
edge("e-3", "program", "answer", f"{CX} {o[0] + o[1]} V{a[0]}")
ly = l[0] + l[1] / 2
edge("e-dsl", "dsl", "llm", f"{SR + 40} {ty + 46} V{ly} H{X0 + SW}")
edge("e-run", "program", "runtime", f"{X0 + SW} {ry} H{SR}", start=True, label="executes")
# evolve: failures that no program over the current vocabulary explains add operators to the DSL
ex = SR + 118
evo = (badge(ex - 68, 112, 3) + text(ex - 4, 114.2, "admit new operators", 6, "end", fill=ACC)
       + text(ex - 4, 121.8, "that serve the incident", 6, "end", fill=ACC))
edge("e-evolve", "runtime", "dsl", f"{ex} {ry - 17} V{ty + 46}", kind="feedback", dash=True, sw=0.72,
     label="stage 3: admit new operators", lab_svg=evo)
# iterate loop, as in the CC figure
lx = X0 - 16
lab = text(lx - 3.5, (ly + ry) / 2, "iterate", 6, fill=ACC, extra=f' transform="rotate(-90 {lx - 3.5} {(ly + ry) / 2})"')
edge("e-iter", "program", "llm", f"{X0} {ry} H{lx} V{ly} H{X0}", kind="feedback", dash=True, sw=0.72,
     label="iterate", lab_svg=lab)

# ---- stage notes beside the loop: progressive expressivity
sx, sy = 8, 116
notes = text(sx, sy, "escalate only if unsatisfied:", 6, "start", fill=MUTED)
for i, s in enumerate(["pick a playbook", "compose a new DAG", "evolve operators"]):
    yy = sy + 10 + i * 9
    notes += badge(sx + 3.8, yy - 2.1, i + 1) + text(sx + 10, yy, s, 6, "start", fill=INK)
ann.append(dict(id="stages", kind="callout", text="1 pick a playbook / 2 compose a new DAG / 3 evolve operators"))
body.append(f'<g id="a:stages" data-kind="annotation">{notes}</g>')
ann.append(dict(id="title", kind="label", text="LegoRCA as Constrained Creativity"))
body.append(f'<g id="a:title" data-kind="annotation">{text(CX, 13, "LegoRCA as Constrained Creativity", 8, fill=ACC, bold=True)}</g>')

defs = ('<defs><marker id="ah" viewBox="0 0 5 4" refX="5" refY="2" markerWidth="5" markerHeight="4" markerUnits="userSpaceOnUse" orient="auto">'
        f'<path d="M0 0 L5 2 L0 4 z" fill="{ACC}"/></marker>'
        '<marker id="as" viewBox="0 0 5 4" refX="0" refY="2" markerWidth="5" markerHeight="4" markerUnits="userSpaceOnUse" orient="auto">'
        f'<path d="M5 0 L0 2 L5 4 z" fill="{ACC}"/></marker></defs>')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}pt" height="{H}pt" '
       f"font-family=\"'TeX Gyre Heros', 'Helvetica Neue', Helvetica, Arimo, Arial, sans-serif\" font-size=\"7\" "
       f'data-spec="cc-instantiations" data-spec-version="1"><rect width="{W}" height="{H}" fill="#ffffff"/>{defs}'
       f'{"".join(back)}{"".join(body)}</svg>')
open("fig.svg", "w").write(svg)
spec = {"meta": {"id": "cc-instantiations", "title": "LegoRCA as Constrained Creativity", "kind": "mechanism",
                 "figure_kind": "mechanism", "column": "double", "width_pt": W, "max_height_pt": H, "template": "mechanism",
                 "direction": "top-down", "palette": "custom", "font": "helvetica", "step_markers": "circled-numbers",
                 "language": "en", "version": 1,
                 "mechanism": {"group": "anatomy", "groups": [], "worked_example": False, "base": "flowchart",
                               "arrangement": "single", "delta_marking": "none", "zoom_callout": False,
                               "notes": "clone of the CC panel in figs/freeform-vs-cc, boxes keep CC role titles; LegoRCA instance as sublabels"},
                 "caption_draft": "LegoRCA instantiates Constrained Creativity: each box keeps its role from Fig. X and shows LegoRCA's instance."},
        "style_overrides": {"palette_roles": {"module": LLMF, "stroke": INK, "text": INK, "accent": ACC, "x-accent_fill": PALE}},
        "nodes": nodes, "edges": edges, "annotations": ann}
json.dump(spec, open("spec.json", "w"), indent=1)
