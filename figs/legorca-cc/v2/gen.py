import json
# Clone of the CC panel in figs/freeform-vs-cc; each box = CC role title + one LegoRCA example.
ACC, PALE, INK, MUTED, LLMF = "#C2410C", "#FDEBDD", "#262626", "#5a5a5a", "#e7e7e7"
W, H = 309, 202
X0, SW = 32, 140
SR, SWS = 190, 114
CX = X0 + SW / 2
ROW = dict(task=(22, 26), llm=(64, 26), out=(106, 42), ans=(166, 28))
nodes, edges, ann, body, back = [], [], [], [], []

def rect(x, y, w, h, fill, stroke, sw=0.72, rx=1.5):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def text(x, y, s, size=6, anchor="middle", fill=INK, bold=False, extra=""):
    b = ' font-weight="bold"' if bold else ''
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{b}{extra}>{s}</text>'
def chip(x, yc, s):
    w = {"find change point": 45.4, "filter": 11.3, "aggregate": 26.8, "compare": 23.2, "rank candidates": 42.1}[s] + 6
    return rect(x, yc - 5, w, 10, "#ffffff", ACC, 0.6, 2) + text(x + w / 2, yc + 2.1, s, 6, fill=ACC), w
def chips(x, yc, names, gap):
    out = ""
    for n in names:
        svg, w = chip(x, yc, n); out += svg; x += w + gap
    return out, x
def node(nid, title, sub, x, y, w, h, fill, stroke, tfill=INK, sfill=MUTED, pict="", role="novel"):
    nodes.append({k: v for k, v in dict(id=nid, label=title, sublabel=sub, kind="module", role=role).items() if v})
    cx = x + w / 2
    t = text(cx, y + 10.5, title, 7, fill=tfill, bold=True)
    if sub: t += text(cx, y + 20, sub, 6, fill=sfill)
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

y, h = ROW["task"]; node("task", "Task", "“Why did login failures spike at 10am?”", X0, y, SW, h, "#ffffff", INK, role="existing")
y, h = ROW["llm"];  node("llm", "LLM", "picks a playbook or composes a new DAG", X0, y, SW, h, LLMF, INK, role="existing")
# DSL program: the composed DAG, as chips joined by arrows
y, h = ROW["out"]; yc = y + 28
names = ["find change point", "filter", "rank candidates"]
ws = [45.4 + 6, 11.3 + 6, 42.1 + 6]; gap = 8
x = CX - (sum(ws) + gap * 2) / 2
pict = ""
for i, (n, w) in enumerate(zip(names, ws)):
    s, _ = chip(x, yc, n); pict += s
    if i < 2: pict += f'<path d="M{x + w + 0.8} {yc} H{x + w + gap - 0.6}" stroke="{ACC}" stroke-width="0.72" marker-end="url(#ah)"/>'
    x += w + gap
node("program", "DSL program", None, X0, y, SW, h, PALE, ACC, pict=f'<g data-symbol="dag">{pict}</g>')
y, h = ROW["ans"]; node("answer", "Answer", "ranked root causes, with evidence", X0, y, SW, h, ACC, ACC, "#ffffff", "#ffffff")

# side column
ty = ROW["task"][0]; dh = 44
def row_w(ns): return sum({"find change point": 45.4, "filter": 11.3, "aggregate": 26.8, "compare": 23.2, "rank candidates": 42.1}[n] + 6 for n in ns) + 3 * (len(ns) - 1)
n1, n2 = ["filter", "aggregate", "compare"], ["find change point", "rank candidates"]
w1 = row_w(n1) + 3 + 6
r1, xe = chips(SR + (SWS - w1) / 2, ty + 22, n1, 3)
r1 += text(xe, ty + 24, "…", 6, "start", fill=ACC)
r2, _ = chips(SR + (SWS - row_w(n2)) / 2, ty + 35, n2, 3)
node("dsl", "DSL / Playbook", None, SR, ty, SWS, dh, PALE, ACC, pict=r1 + r2)
o = ROW["out"]; ry = o[0] + o[1] / 2
node("runtime", "DSL runtime engine", "SQL · statistics · ML, with caching", SR, ry - 13, SWS, 26, PALE, ACC)

t, l, a = ROW["task"], ROW["llm"], ROW["ans"]; ly = l[0] + l[1] / 2
edge("e-1", "task", "llm", f"{CX} {t[0] + t[1]} V{l[0]}")
edge("e-2", "llm", "program", f"{CX} {l[0] + l[1]} V{o[0]}")
edge("e-3", "program", "answer", f"{CX} {o[0] + o[1]} V{a[0]}")
edge("e-dsl", "dsl", "llm", f"{SR + SWS / 2} {ty + dh} V{ly} H{X0 + SW}")
edge("e-run", "program", "runtime", f"{X0 + SW} {ry} H{SR}", start=True, label="executes")
lx = X0 - 16
lab = text(lx - 3.5, (ly + ry) / 2, "iterate", 6, fill=ACC, extra=f' transform="rotate(-90 {lx - 3.5} {(ly + ry) / 2})"')
edge("e-iter", "program", "llm", f"{X0} {ry} H{lx} V{ly} H{X0}", kind="feedback", dash=True, sw=0.72, label="iterate", lab_svg=lab)

ann.append(dict(id="title", kind="label", text="LegoRCA"))
body.append(f'<g id="a:title" data-kind="annotation">{text(CX, 13, "LegoRCA", 8, fill=ACC, bold=True)}</g>')
defs = ('<defs><marker id="ah" viewBox="0 0 5 4" refX="5" refY="2" markerWidth="5" markerHeight="4" markerUnits="userSpaceOnUse" orient="auto">'
        f'<path d="M0 0 L5 2 L0 4 z" fill="{ACC}"/></marker>'
        '<marker id="as" viewBox="0 0 5 4" refX="0" refY="2" markerWidth="5" markerHeight="4" markerUnits="userSpaceOnUse" orient="auto">'
        f'<path d="M5 0 L0 2 L5 4 z" fill="{ACC}"/></marker></defs>')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}pt" height="{H}pt" '
       f"font-family=\"'TeX Gyre Heros', 'Helvetica Neue', Helvetica, Arimo, Arial, sans-serif\" font-size=\"7\" "
       f'data-spec="legorca-cc" data-spec-version="2"><rect width="{W}" height="{H}" fill="#ffffff"/>{defs}'
       f'{"".join(back)}{"".join(body)}</svg>')
open("fig.svg", "w").write(svg)
spec = {"meta": {"id": "legorca-cc", "title": "LegoRCA", "kind": "mechanism", "figure_kind": "mechanism", "column": "single",
                 "width_pt": W, "max_height_pt": H, "template": "mechanism", "direction": "top-down", "palette": "custom",
                 "font": "helvetica", "step_markers": "none", "language": "en", "version": 2,
                 "mechanism": {"group": "anatomy", "groups": [], "worked_example": False, "base": "flowchart",
                               "arrangement": "single", "delta_marking": "none", "zoom_callout": False,
                               "notes": "clone of the CC panel in figs/freeform-vs-cc; one LegoRCA example per box"},
                 "caption_draft": "LegoRCA instantiates Constrained Creativity: the LLM composes RCA operators from the DSL into an analysis DAG that the runtime executes over telemetry, returning ranked root causes with evidence."},
        "style_overrides": {"palette_roles": {"module": LLMF, "stroke": INK, "text": INK, "accent": ACC, "x-accent_fill": PALE}},
        "nodes": nodes, "edges": edges, "annotations": ann}
json.dump(spec, open("spec.json", "w"), indent=1)
