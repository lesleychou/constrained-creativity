# Brief — How applications instantiate Constrained Creativity (confirmed: LegoRCA only, cloned panel, verdicts dropped)

**What.** Mechanism / comparison figure for the blog, double-column (504 pt). Each panel is a copy of the
*right* panel of `freeform-vs-cc` (same boxes, same positions, same arrows, same iterate loop), with every block
relabelled as "CC role → this application's instance". Single panel: LegoRCA. Incalmo section kept below for a later panel (needs the CC preprint to verify).

**Block mapping (CC role → LegoRCA, source: NSDI'27 #768 §3–4, App. C, Fig. 10).**
- Task → KPI alert + baseline / anomalous windows (+ optional analyst hint).
  e.g. "shipping-service avg latency ↑; 13:00–14:00 vs 14:00–14:30".
- DSL / Playbook → D = (G, O): fixed grammar G = loop-free typed DAG
  (load → aggregate → candidates → scored → one ranked answer); vocabulary O = 19 starter operators
  (7 candidate generators, 10 scorers, 2 summarizers) + 11 playbooks, specialised per deployment by Bootstrap.
- LLM → Gemini-3.1-Pro; sees schema + operator signatures + playbooks, never the telemetry.
- DSL program → JSON operator DAG, e.g. Fig. 10: load spans → baseline/incident aggregates →
  obtain_relevant_servers → {entity_rca, stattest_rca, flow_attribution_scorer} → attach_metric_evidence →
  ranked_leads (15 ops).
- DSL runtime engine → verifier (operators exist, types match, acyclic, one answer) + Ray execution engine
  (parallel SQL / ML / stateful ops, cache keyed by recursive input hash), runs locally next to the data.
- Answer → top-5 ranked leads, each with score + evidence, e.g. "frontend-1: container network latency".
- iterate → progressive stages: ① pick playbook → ② compose new DAG → ③ evolve: synthesise operators,
  admitted only if they serve the incident (the loop can also extend the DSL's vocabulary).

**Block mapping (CC role → Incalmo, source: Incalmo S&P'26 — from memory, TO VERIFY).**
- Task → attack goal in a multi-host network (e.g. exfiltrate the database from an internal host).
- DSL / Playbook → high-level actions: scan(network), lateral_move(src, dst), escalate_privilege(host),
  find_information(host), exfiltrate_data(host).
- DSL program → sequence of high-level actions chosen step by step.
- DSL runtime engine → action planner (translates each action to low-level commands / exploits) +
  environment state service + attack graph service.
- Answer → goals achieved, with the action log / attack path as evidence.
- iterate → observe updated environment state, choose next action.

**Point.** The abstract CC skeleton is unchanged; only the contents of the boxes change per application.

**Assumptions to confirm.** (1) Applications shown. (2) Layout: one panel per application, identical to the CC panel.
(3) Verdict list (✓ Expressive …) replaced by each paper's headline number, or dropped.
