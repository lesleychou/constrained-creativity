# Brief — Fig. 1 (blog): Unconstrained AI vs. Constrained Creativity

**What.** Opening figure of the blog post "Making Agents More Reliable with Constrained Creativity" (also usable in
the HotNets paper). A mechanism *comparison*: the same task handled by an LLM with complete freedom (left) vs. an
LLM restricted to composing a verifiable DSL (right). Double-column width (~504 pt), minimal style.

**What is drawn.** Two side-by-side panels on one aligned, top-down template: Input → LLM → what the LLM emits →
Output, closed by a three-row scorecard. Generic task (user choice); RCA is one instance.
- (a) **Unconstrained AI** (baseline): Input **Task + all raw data** → **LLM** → **Arbitrary code** (no checks) → Output **Unchecked answer**.
- (b) **Constrained Creativity** (ours): Input **Task** + **DSL** (operators + structure) → **LLM** →
  **DSL program** (small DAG of operators) → **Verifier** (dashed retry back to LLM: "verified = false") →
  **Runtime engine** (reads **Data**, executes the verified program) → Output **Verified answer**.
- What differs: the DSL constraint, the verifier, and that data goes to the runtime instead of the prompt.

**Story.** Read left top-down: everything is stuffed into the prompt, the LLM writes anything, nothing is checked.
Read right top-down: the LLM sees only the alert + DSL, emits a small program, the verifier gates it, the runtime
executes it over telemetry.

**Point.** Same LLM, same task — constraining its action space buys reliability (verified), accuracy and
cost. The eye lands on the accent-coloured DSL/Verifier path and the scorecard.

**Scorecard (qualitative, user choice):** Reliability ✗ unverifiable / ✓ verified; Accuracy ✗ low / ✓ high; Cost ✗ high / ✓ low.

**Layout.** Mechanism / comparison, panels-row ×2, aligned template, no legend, no step numbers. Grey for the
baseline, one accent (teal, matching the paper's Fig. 3 "LLM + constraints" colour) for the constrained path.
Exemplars: asplos25-038_fig1 (identical chain + verdict line per panel), asplos25-006_fig1 (colour marks the delta).

**Caption draft.** Figure 1. Left: an unconstrained agent receives the alert with the full telemetry and may emit
arbitrary code; nothing checks its answer. Right: with constrained creativity, the LLM composes a program from a
DSL of domain operators; a verifier checks it (retrying on failure) and a runtime engine executes it over the
telemetry. On root cause analysis, the same LLM is 9× more accurate while using 12.5× fewer tokens.
