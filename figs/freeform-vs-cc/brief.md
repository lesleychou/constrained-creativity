# Brief — Free-form LLM vs. Constrained Creativity (from the whiteboard sketch `sketch.png`)

**What.** Abstract mechanism *comparison* for the blog: the same task handled by a free-form LLM (left) and by
Constrained Creativity (right). Double-column (504 pt), minimal, faithful to the hand drawing.

**Shared skeleton (identical rows, identical positions in both panels):** Task → LLM → *what the LLM emits* → Answer,
with an "iterate" loop from the LLM's output back to the LLM.

**What differs.**
- Left: LLM emits **arbitrary programs / text** (drawn as scattered, irregular fragments). Answer has no evidence.
- Right: **DSL / Playbook** is an extra input to the LLM; LLM emits a **DSL program** (drawn as a neat DAG of
  building blocks) that runs on a **DSL runtime engine** (two-way arrow); answer is **explained, with evidence**.
- Verdict beside each answer: left ✓ Expressive ✗ Explainable ✗ Effective ✗ Efficient; right ✓ on all four.

**Point.** Same task, same LLM, same iterate loop, both expressive; the DSL + runtime is what buys explainability,
effectiveness and efficiency. Everything new is drawn in the single accent (blog orange #C2410C), the rest grey.

**Assumptions.** (1) Side notes from the sketch (data servers, "agent's code ⇄ py sandbox") are dropped as the
user's description omits them. (2) Iteration on the right loops from the DSL program (whose run results come back
from the runtime) to the LLM. (3) No Input/Output row labels; Task and Answer are self-explanatory.

**Caption draft.** Free-form LLM agents (left) emit arbitrary code or text: expressive, but hard to explain, unreliable
and costly. With Constrained Creativity (right), the LLM writes programs in a DSL of safe building blocks that a
dedicated runtime executes, so answers stay expressive and come with evidence.
