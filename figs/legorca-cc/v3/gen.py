import json
# v3: clone of the CC panel in figs/freeform-vs-cc, minimal text + one icon per box.
# Operators are drawn as Lego bricks: the DSL holds the bricks, the program snaps a few of them together.
ACC, PALE, INK, MUTED, LLMF = "#C2410C", "#FDEBDD", "#262626", "#5a5a5a", "#e7e7e7"
W, H = 262, 184
X0, SW = 30, 110
SR, SWS = 164, 92
CX = X0 + SW / 2
ROW = dict(task=(22, 26), llm=(62, 20), out=(98, 34), ans=(150, 26))
TW = {"Task": 15.2, "LLM": 13.6, "DSL program": 41.6, "Answer": 23.4, "DSL / Playbook": 48.3, "DSL runtime engine": 61.9}
BW = {"filter": 11.3, "compare": 23.2, "rank": 11.6}
nodes, edges, ann, body, back = [], [], [], [], []

def rect(x, y, w, h, fill, stroke, sw=0.72, rx=1.5):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def text(x, y, s, size=6, anchor="middle", fill=INK, bold=False, extra=""):
    b = ' font-weight="bold"' if bold else ''
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{b}{extra}>{s}</text>'

# --- icons, drawn on a 16-unit grid (brain, gear, magnifier from assets/symbols; spike chart drawn here)
ICONS = {
    "spike": '<path d="M2 2V14H14"/><path d="M2.8 11.2 L5 10.2 L7 10.9 L9 3.8 L10.6 10.3 L13.6 9.6"/>',
    "brain": ('<path d="M8 2.6C6.3 1.3 3.6 2 3.2 4.1C1.8 4.7 1.6 6.7 2.8 7.7C2 9.2 3 11.2 4.8 11.6C5.2 13.4 7.3 14 8 12.8'
              'C8.7 14 10.8 13.4 11.2 11.6C13 11.2 14 9.2 13.2 7.7C14.4 6.7 14.2 4.7 12.8 4.1C12.4 2 9.7 1.3 8 2.6Z"/>'
              '<path d="M8 2.6V12.8"/><path d="M5.4 5.2C6.7 5.6 6.7 7.1 5.4 7.6"/><path d="M10.6 8.4C9.3 8.8 9.3 10.3 10.6 10.8"/>'),
    "gear": ('<path d="M14.49 6.81 14.49 9.19 12.48 9.42 12.17 10.17 13.43 11.75 11.75 13.43 10.17 12.17 9.42 12.48 9.19 14.49 '
             '6.81 14.49 6.58 12.48 5.83 12.17 4.25 13.43 2.57 11.75 3.83 10.17 3.52 9.42 1.51 9.19 1.51 6.81 3.52 6.58 3.83 5.83 '
             '2.57 4.25 4.25 2.57 5.83 3.83 6.58 3.52 6.81 1.51 9.19 1.51 9.42 3.52 10.17 3.83 11.75 2.57 13.43 4.25 12.17 5.83 '
             '12.48 6.58Z"/><circle cx="8" cy="8" r="2.1"/>'),
    "magnifier": '<circle cx="6.6" cy="6.6" r="4.4"/><path d="M9.8 9.8L14.2 14.2"/>',
    "brick": '<rect x="1.5" y="6" width="13" height="7.5" rx="0.8"/><rect x="3.5" y="3.6" width="3" height="2.4"/><rect x="9.5" y="3.6" width="3" height="2.4"/>',
}
def icon(name, x, y, s, col):
    k = s / 16
    extra = f'<circle cx="9" cy="3.8" r="1.3" fill="{ACC}" stroke="none"/>' if name == "spike" else ""
    return (f'<g data-symbol="{name}" transform="translate({x} {y}) scale({k})" fill="none" stroke="{col}" '
            f'stroke-width="{0.75 / k:.2f}" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}{extra}</g>')

def brick(x, yc, s):
    """An operator drawn as a Lego brick: label box with two studs on top."""
    w = BW[s] + 6
    studs = "".join(f'<rect x="{x + w * f - 1.6}" y="{yc - 6.3}" width="3.2" height="1.8" rx="0.4" fill="{ACC}"/>' for f in (0.28, 0.72))
    return studs + rect(x, yc - 4.5, w, 9, "#ffffff", ACC, 0.6, 1) + text(x + w / 2, yc + 2.1, s, 6, fill=ACC), w

def node(nid, title, x, y, w, h, fill, stroke, ic=None, sub=None, tfill=INK, sfill=MUTED, icol=INK, pict="", role="novel", ty=None):
    nodes.append({k: v for k, v in dict(id=nid, label=title, sublabel=sub, kind="module", role=role).items() if v})
    cx = x + w / 2
    if ty is None: ty = y + 10.5 if (sub or pict) else y + h / 2 + 2.5
    s = 11; gap = 2.5
    if ic:
        tot = s + gap + TW[title]; x0 = cx - tot / 2
        t = icon(ic, x0, ty - 8.4, s, icol) + text(x0 + s + gap, ty, title, 7, "start", fill=tfill, bold=True)
    else:
        t = text(cx, ty, title, 7, fill=tfill, bold=True)
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

# ---- skeleton
y, h = ROW["task"]; node("task", "Task", X0, y, SW, h, "#ffffff", INK, ic="spike", sub="login failures ↑ at 10am", role="existing")
y, h = ROW["llm"];  node("llm", "LLM", X0, y, SW, h, LLMF, INK, ic="brain", role="existing")
y, h = ROW["out"]; yc = y + 24.5
names, gap = ["filter", "compare", "rank"], 8
x = CX - (sum(BW[n] + 6 for n in names) + gap * 2) / 2
pict = ""
for i, n in enumerate(names):
    s, w = brick(x, yc, n); pict += s
    if i < 2: pict += f'<path d="M{x + w + 0.8} {yc} H{x + w + gap - 0.6}" stroke="{ACC}" stroke-width="0.72" marker-end="url(#ah)"/>'
    x += w + gap
node("program", "DSL program", X0, y, SW, h, PALE, ACC, pict=f'<g data-symbol="brick-chain">{pict}</g>')
y, h = ROW["ans"]; node("answer", "Answer", X0, y, SW, h, ACC, ACC, ic="magnifier", sub="ranked root causes",
                        tfill="#ffffff", sfill="#ffffff", icol="#ffffff")

# ---- side column
ty0, dh = ROW["task"][0], 32
bricks, x = "", None
row = ["filter", "compare", "rank"]
tot = sum(BW[n] + 6 for n in row) + 4 * 3 + 6
x = SR + (SWS - tot) / 2
for n in row:
    s, w = brick(x, ty0 + 23, n); bricks += s; x += w + 4
bricks += text(x, ty0 + 25, "…", 6, "start", fill=ACC)
node("dsl", "DSL / Playbook", SR, ty0, SWS, dh, PALE, ACC, pict=bricks)
o = ROW["out"]; ry = o[0] + o[1] / 2
node("runtime", "DSL runtime engine", SR, ry - 10, SWS, 20, PALE, ACC, ic="gear", icol=ACC)

t, l, a = ROW["task"], ROW["llm"], ROW["ans"]; ly = l[0] + l[1] / 2
edge("e-1", "task", "llm", f"{CX} {t[0] + t[1]} V{l[0]}")
edge("e-2", "llm", "program", f"{CX} {l[0] + l[1]} V{o[0]}")
edge("e-3", "program", "answer", f"{CX} {o[0] + o[1]} V{a[0]}")
edge("e-dsl", "dsl", "llm", f"{SR + SWS / 2} {ty0 + dh} V{ly} H{X0 + SW}")
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
       f'data-spec="legorca-cc" data-spec-version="3"><rect width="{W}" height="{H}" fill="#ffffff"/>{defs}'
       f'{"".join(back)}{"".join(body)}</svg>')
open("fig.svg", "w").write(svg)
spec = {"meta": {"id": "legorca-cc", "title": "LegoRCA", "kind": "mechanism", "figure_kind": "mechanism", "column": "single",
                 "width_pt": W, "max_height_pt": H, "template": "mechanism", "direction": "top-down", "palette": "custom",
                 "font": "helvetica", "step_markers": "none", "language": "en", "version": 3,
                 "mechanism": {"group": "anatomy", "groups": [], "worked_example": False, "base": "flowchart",
                               "arrangement": "single", "delta_marking": "none", "zoom_callout": False,
                               "notes": "clone of the CC panel in figs/freeform-vs-cc; one icon + at most one short line per box; operators drawn as Lego bricks"},
                 "caption_draft": "LegoRCA instantiates Constrained Creativity: the LLM snaps RCA operators from the DSL into an analysis program that the runtime executes over telemetry, returning ranked root causes with evidence."},
        "style_overrides": {"palette_roles": {"module": LLMF, "stroke": INK, "text": INK, "accent": ACC, "x-accent_fill": PALE}},
        "nodes": nodes, "edges": edges, "annotations": ann}
json.dump(spec, open("spec.json", "w"), indent=1)
