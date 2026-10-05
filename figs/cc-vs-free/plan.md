# Plan — cc-vs-free (504 × 246 pt, double column)
- Panels: left "Unconstrained AI" centred x=112, right "Constrained Creativity" centred x=392; a centre gutter (x=252)
  carries row labels **Input / Output** and the scorecard rows **Reliability / Accuracy / Cost**.
- Rows (top-down, aligned across panels): Input y22–46 · LLM y58–74 · action y86–108 · verify y120–136 ·
  runtime y148–164 · Output y176–192 · rule y202 · scorecard baselines 214/226/238.
- Left: Task + all raw data (in the prompt) → LLM → Arbitrary code → long grey arrow "no verification" → Unchecked answer.
  The empty verify/runtime rows are the point.
- Right: Task + DSL (operators + structure) → LLM → DSL program (mini DAG glyph) → Verifier → Runtime engine ← Data
  → Verified answer; dashed teal "retry if invalid" Verifier → LLM (only dashed meaning in the figure).
- Colour: palette cool-grey-cyan. LLM grey #e7e7e7 both sides (same model). Baseline boxes #f2f2f2/#8c8c8c.
  Ours #c5e5e5/#117788; Verified answer is the single accent (#117788, white text). ✓ teal, ✗ #c00000 (drawn as paths).
- Type: 8 bold titles, 7 labels, 6 sublabels. Strokes 0.72; right main path 1.0 teal, left arrows grey 0.72.
- Check list: (1) inputs/outputs read at a glance on both sides; (2) rows aligned across panels; (3) right path is
  the loudest thing; (4) retry loop clear of labels and Data box; (5) scorecard cells aligned with gutter labels;
  (6) nothing below 6 pt.
