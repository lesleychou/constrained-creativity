import json
# v4: GPT sketch's organisation (one row per CC block: block on the left, a small example on the right),
# block names and colours from the CC figure (figs/freeform-vs-cc), 2-3 example items per block.
ACC, PALE, INK, MUTED, LLMF, EXF, CHIPG = "#C2410C", "#FDEBDD", "#262626", "#5a5a5a", "#e7e7e7", "#f4f4f4", "#9a9a9a"
MONO = "'DejaVu Sans Mono', Menlo, Consolas, 'Courier New', monospace"
W = 290
X0, LW = 26, 96              # block column
RX, RW = 130, 152            # example column
GAP = 9
HEIGHTS = [("task", 22), ("dsl", 22), ("llm", 22), ("program", 32), ("runtime", 22), ("answer", 34)]
ROW, y = {}, 24
for k, h in HEIGHTS:
    ROW[k] = (y, h); y += h + GAP
H = y - GAP + 6
LCX = X0 + LW / 2
nodes, edges, ann, body, back = [], [], [], [], []

def rect(x, y, w, h, fill, stroke="none", sw=0.72, rx=1.5):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def text(x, y, s, size=6, anchor="middle", fill=INK, bold=False, extra=""):
    b = ' font-weight="bold"' if bold else ''
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{b}{extra}>{s}</text>'

ICONS = {
    "spike": '<path d="M2 2V14H14"/><path d="M2.8 11.2 L5 10.2 L7 10.9 L9 3.8 L10.6 10.3 L13.6 9.6"/>',
    "brick": ('<rect x="1.5" y="9" width="13" height="5" rx="0.6"/><rect x="3.5" y="3.5" width="9" height="5.5" rx="0.6"/>'
              '<path d="M5 3.5V2.2H7V3.5M9 3.5V2.2H11V3.5"/>'),
    "brain": ('<path d="M8 2.6C6.3 1.3 3.6 2 3.2 4.1C1.8 4.7 1.6 6.7 2.8 7.7C2 9.2 3 11.2 4.8 11.6C5.2 13.4 7.3 14 8 12.8'
              'C8.7 14 10.8 13.4 11.2 11.6C13 11.2 14 9.2 13.2 7.7C14.4 6.7 14.2 4.7 12.8 4.1C12.4 2 9.7 1.3 8 2.6Z"/>'
              '<path d="M8 2.6V12.8"/><path d="M5.4 5.2C6.7 5.6 6.7 7.1 5.4 7.6"/><path d="M10.6 8.4C9.3 8.8 9.3 10.3 10.6 10.8"/>'),
    "dag": ('<circle cx="8" cy="3.4" r="2"/><circle cx="3.4" cy="12.4" r="2"/><circle cx="12.6" cy="12.4" r="2"/>'
            '<path d="M7 5.2L4.4 10.6M9 5.2L11.6 10.6M5.4 12.4H10.6"/>'),
    "gear": ('<path d="M14.49 6.81 14.49 9.19 12.48 9.42 12.17 10.17 13.43 11.75 11.75 13.43 10.17 12.17 9.42 12.48 9.19 14.49 '
             '6.81 14.49 6.58 12.48 5.83 12.17 4.25 13.43 2.57 11.75 3.83 10.17 3.52 9.42 1.51 9.19 1.51 6.81 3.52 6.58 3.83 5.83 '
             '2.57 4.25 4.25 2.57 5.83 3.83 6.58 3.52 6.81 1.51 9.19 1.51 9.42 3.52 10.17 3.83 11.75 2.57 13.43 4.25 12.17 5.83 '
             '12.48 6.58Z"/><circle cx="8" cy="8" r="2.1"/>'),
    "magnifier": '<circle cx="6.6" cy="6.6" r="4.4"/><path d="M9.8 9.8L14.2 14.2"/>',
}
def icon(name, x, y, s, col):
    k = s / 16
    extra = f'<circle cx="9" cy="3.8" r="1.3" fill="{ACC}" stroke="none"/>' if name == "spike" else ""
    return (f'<g data-symbol="{name}" transform="translate({x} {y}) scale({k})" fill="none" stroke="{col}" '
            f'stroke-width="{0.75 / k:.2f}" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}{extra}</g>')

TWIDTH = {"find change point": 45.4, "filter": 11.3, "rank candidates": 42.1, "SQL": 12.0, "statistics": 23.0, "ML": 8.3}
def chips(x, yc, names, stroke, tcol, gap=3, more=False):
    out = ""
    for n in names:
        w = TWIDTH[n] + 6
        out += rect(x, yc - 4.5, w, 9, "#ffffff", stroke, 0.6, 4.5) + text(x + w / 2, yc + 2.1, n, 6, fill=tcol)
        x += w + gap
    if more: out += text(x + 1, yc + 2.1, "…", 6, "start", fill=tcol)
    return out

def row(nid, title, ic, fill, stroke, tfill, icol, example, role="novel"):
    y, h = ROW[nid]
    nodes.append(dict(id=nid, label=title, kind="module", role=role))
    cy = y + h / 2
    blk = rect(X0, y, LW, h, fill, stroke) + icon(ic, X0 + 7, cy - 5.5, 11, icol) + text(X0 + 23, cy + 2.5, title, 7, "start", fill=tfill, bold=True)
    body.append(f'<g id="n:{nid}" data-kind="node" data-role="{role}">{blk}</g>')
    ann.append(dict(id=f"{nid}-ex", kind="callout", text=f"example: {title}"))
    body.append(f'<g id="a:{nid}-ex" data-kind="annotation">{rect(RX, y, RW, h, EXF, rx=2)}{example(y, h, cy)}</g>')

def edge(eid, frm, to, d, kind="data", dash=False, label=None, lab_svg="", sw=1.0):
    e = {"id": eid, "from": frm, "to": to, "kind": kind}
    if dash: e["style"] = "dashed"
    if label: e["label"] = label
    edges.append(e)
    da = ' stroke-dasharray="2.5 1.9"' if dash else ''
    back.append(f'<g id="e:{eid}" data-kind="edge" data-from="{frm}" data-to="{to}" data-edge-kind="{kind}">'
                f'<path d="M{d}" fill="none" stroke="{ACC}" stroke-width="{sw}"{da} marker-end="url(#ah)"/>{lab_svg}</g>')

EX = RX + 7
row("task", "Task", "spike", "#ffffff", INK, INK, INK,
    lambda y, h, cy: text(EX, cy + 2.1, "“Why did login failures spike at 10am?”", 6, "start"), role="existing")
row("dsl", "DSL / Playbook", "brick", PALE, ACC, INK, ACC,
    lambda y, h, cy: chips(EX, cy, ["find change point", "filter", "rank candidates"], ACC, ACC, more=True))
row("llm", "LLM", "brain", LLMF, INK, INK, INK,
    lambda y, h, cy: text(EX, cy + 2.1, "pick a playbook, or compose a new DAG", 6, "start"), role="existing")
CODE = [("c", "find_change_point", "(kpi)"), ("f", "filter", "(c, service)"), ("r", "rank_candidates", "(f)")]
def code(y, h, cy):
    out = ""
    for i, (v, op, args) in enumerate(CODE):
        out += (f'<text x="{EX}" y="{y + 10 + i * 8}" font-size="6" font-family="{MONO}" fill="{INK}">{v} = '
                f'<tspan fill="{ACC}">{op}</tspan>{args}</text>')
    return out
row("program", "DSL program", "dag", PALE, ACC, INK, ACC, code)
row("runtime", "DSL runtime engine", "gear", PALE, ACC, INK, ACC,
    lambda y, h, cy: chips(EX, cy, ["SQL", "statistics", "ML"], CHIPG, MUTED))
def answer(y, h, cy):
    # mini KPI plot with the spike, then a ranked list (#1 spelled out, the rest as grey bars)
    px, pw = EX, 46
    pts = [(0, .62), (.1, .55), (.2, .66), (.3, .58), (.4, .64), (.5, .56), (.6, .62), (.7, .1), (.8, .6), (.9, .55), (1, .6)]
    d = " ".join(f'{"M" if i == 0 else "L"}{px + 2 + x * (pw - 4):.1f} {y + 5 + v * (h - 12):.1f}' for i, (x, v) in enumerate(pts))
    sx, sy = px + 2 + .7 * (pw - 4), y + 5 + .1 * (h - 12)
    plot = (f'<path d="M{px} {y + 4}V{y + h - 5}H{px + pw}" fill="none" stroke="{CHIPG}" stroke-width="0.6"/>'
            f'<path d="{d}" fill="none" stroke="{MUTED}" stroke-width="0.6"/><circle cx="{sx:.1f}" cy="{sy:.1f}" r="1.5" fill="{ACC}"/>')
    lx = px + pw + 9
    lst = text(lx, y + 11, "1", 6, "start", fill=ACC, bold=True) + text(lx + 6, y + 11, "clients in region R", 6, "start")
    for i, w in enumerate([44, 32]):
        yy = y + 19 + i * 7
        lst += text(lx, yy + 2, str(i + 2), 6, "start", fill=MUTED) + rect(lx + 6, yy - 1.2, w, 2.4, "#d4d4d4", rx=1.2)
    return plot + lst
row("answer", "Answer", "magnifier", ACC, ACC, "#ffffff", "#ffffff", answer)

order = [k for k, _ in HEIGHTS]
for a, b in zip(order, order[1:]):
    ya, ha = ROW[a]; yb, _ = ROW[b]
    edge(f"e-{a}-{b}", a, b, f"{LCX} {ya + ha} V{yb}")
ly = ROW["llm"][0] + ROW["llm"][1] / 2; ry = ROW["runtime"][0] + ROW["runtime"][1] / 2
lx = X0 - 13
lab = text(lx - 3.5, (ly + ry) / 2, "iterate", 6, fill=ACC, extra=f' transform="rotate(-90 {lx - 3.5} {(ly + ry) / 2})"')
edge("e-iter", "runtime", "llm", f"{X0} {ry} H{lx} V{ly} H{X0}", kind="feedback", dash=True, sw=0.72, label="iterate", lab_svg=lab)

ann.append(dict(id="title", kind="label", text="LegoRCA: root cause analysis via Constrained Creativity"))
body.append(f'<g id="a:title" data-kind="annotation">{text(W / 2, 13, "LegoRCA: root cause analysis via Constrained Creativity", 8, fill=ACC, bold=True)}</g>')
defs = ('<defs><marker id="ah" viewBox="0 0 5 4" refX="5" refY="2" markerWidth="5" markerHeight="4" markerUnits="userSpaceOnUse" orient="auto">'
        f'<path d="M0 0 L5 2 L0 4 z" fill="{ACC}"/></marker></defs>')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}pt" height="{H}pt" '
       f"font-family=\"'TeX Gyre Heros', 'Helvetica Neue', Helvetica, Arimo, Arial, sans-serif\" font-size=\"7\" "
       f'data-spec="legorca-cc" data-spec-version="4"><rect width="{W}" height="{H}" fill="#ffffff"/>{defs}'
       f'{"".join(back)}{"".join(body)}</svg>')
open("fig.svg", "w").write(svg)
spec = {"meta": {"id": "legorca-cc", "title": "LegoRCA: root cause analysis via Constrained Creativity", "kind": "mechanism",
                 "figure_kind": "mechanism", "column": "single", "width_pt": W, "max_height_pt": H, "template": "mechanism",
                 "direction": "top-down", "palette": "custom", "font": "helvetica", "step_markers": "none", "language": "en", "version": 4,
                 "mechanism": {"group": "anatomy", "groups": [], "worked_example": True, "base": "flowchart", "arrangement": "single",
                               "delta_marking": "none", "zoom_callout": False,
                               "notes": "GPT sketch organisation: CC block per row on the left, one small example on the right"},
                 "caption_draft": "LegoRCA instantiates each block of Constrained Creativity; the right column shows one example per block."},
        "style_overrides": {"palette_roles": {"module": LLMF, "stroke": INK, "text": INK, "accent": ACC, "x-accent_fill": PALE}},
        "nodes": nodes, "edges": edges, "annotations": ann}
json.dump(spec, open("spec.json", "w"), indent=1)
