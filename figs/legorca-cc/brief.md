# Brief — LegoRCA in the CC layout (v2: minimal text)

Clone of the right panel of `figs/freeform-vs-cc` (same boxes, positions, arrows, iterate loop, palette). Each box
keeps its CC role as the title and carries ONE short LegoRCA example, taken from the GPT sketch the user supplied:
- Task: "Why did login failures spike at 10am?"
- DSL / Playbook: operator chips — filter · aggregate · compare · find change point · rank candidates · …
- LLM: picks a playbook or composes a new DAG
- DSL program: DAG of chips find change point → filter → rank candidates
- DSL runtime engine: SQL · statistics · ML, with caching
- Answer: ranked root causes, with evidence
Dropped vs v1 (`figs/cc-instantiations`): verdicts, stage notes, evolve arrow, model/operator counts.
Note: the chip operator names are illustrative (from the GPT sketch), not LegoRCA's real operator ids.
