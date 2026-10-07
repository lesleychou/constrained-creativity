---
title: Making Agents More Reliable with Constrained Creativity
subtitle: The counterintuitive path to more capable, lower-cost AI
date: 2026-10-07
authors: [lesley-zhou, vyas-sekar]
research: https://kilthub.cmu.edu/articles/preprint/Constrained_Creativity_for_SysOps_Agents/33138296
researchers:
  - { name: Sayan Sinha, website: "https://americast.github.io/" }
  - { name: Vipul Harsh, website: "https://vipulharsh.github.io/" }
  - lesley-zhou
  - marko-morrison
  - { name: B. Aditya Prakash, website: "https://cse.gatech.edu/people/b-aditya-prakash" }
  - { name: Hui Zhang, website: "https://www.cs.cmu.edu/~hzhang/" }
  - vyas-sekar
description: Giving AI agents unlimited freedom makes them expensive and hard to verify. Constrained Creativity lets the agent be creative only within a domain-specific language of verifiable building blocks, improving reliability and accuracy while cutting cost.
---

<div class="callout tldr">
  <p class="tldr-label">TL;DR</p>
  <ul>
    <li>AI agents are getting more capable, but reliability in high-stakes systems still sucks.</li>
    <li>We propose <strong>Constrained Creativity</strong>: give agents the least freedom they need, using a DSL of safe building blocks, and expand that space only when necessary.</li>
    <li>In root cause analysis and cyber red-teaming, Constrained Creativity makes agents more accurate, easier to verify, and far cheaper than free-form agents.</li>
  </ul>
</div>

<div class="figure figure-image figure-card"><img src="{{ '/assets/img/posts/constrained-creativity/freeform-vs-cc.png' | relative_url }}" alt="Side-by-side comparison. Left, Free-form LLM: a task goes to an LLM that iterates on arbitrary programs or text and returns an answer with no evidence; it is expressive but not explainable, effective or efficient. Right, Constrained Creativity: the task and a DSL or playbook feed the LLM, which iterates on a DSL program executed by a DSL runtime engine and returns an answer with evidence; it is expressive, explainable, effective and efficient."></div>

<p class="figure-caption figure-caption-center"><strong>Fig. 1.</strong> Constrained Creativity may look counterintuitive at first: constraints seem like they would limit AI’s utility. But in many domains, unbounded creativity is actually counterproductive. Jazz is a classic example, where structural constraints help enable creative musical expression.</p>

AI agents are getting more capable and knowledgeable, but these capabilities have not been translated into reliability. It is fundamentally difficult for AI agents to be general purpose and fully automated at the same time in high-stakes applications, where reliability must come first (see [Arvind Narayanan’s keynote](https://www.cs.princeton.edu/~arvindn/talks/icml-2026-annotated-slides/) [[2]](#ref-2)).
<!-- TODO: the draft says "refer to Arvind's original post" — swap the link if you meant a different post. -->

We see this tension first-hand in systems, networking, and cybersecurity. For example, in system root cause analysis (RCA), the agent must handle very different failures, from unusual user groups to subtle event sequences. In network management, operator requests are diverse and unpredictable, and AI-generated programs must obey strict network invariants. In cybersecurity, autonomous attackers need to coordinate many steps across many machines. Across all of these applications, we found that free-form coding agents can be expensive and hard to verify.

### Our idea: constrain the space in which AI is allowed to be creative

We propose a different philosophy for building AI agents: **Constrained Creativity** [[1]](#ref-1). Instead of letting AI act arbitrarily, we give AI the least freedom it needs, and only expand that space when necessary.

<div class="figure figure-image figure-card"><img src="{{ '/assets/img/posts/constrained-creativity/freedom-spectrum.png' | relative_url }}" style="width: min(100%, 520px)" alt="Nested boxes showing four levels of agent freedom: (1) fixed playbooks, (2) flexible playbooks with fixed operators and DSL, (3) flexible playbooks and operators with a fixed DSL, (4) arbitrary analysis. An axis below runs from more explainable to more expressive."></div>

<p class="figure-caption figure-caption-center"><strong>Fig. 2.</strong> How much freedom to give the agent, from fixed playbooks (most explainable) to arbitrary analysis (most expressive).</p>

A key part of Constrained Creativity is choosing ***how much freedom to give the AI***. More constraints make the agent easier to understand and verify, but they also limit what it can do. At one extreme, we can give the agent a fixed playbook. This is easy to trust, but it only handles situations we already anticipated. At the other extreme, we can let the agent write arbitrary analysis code. This gives maximum flexibility, but its behavior becomes much harder to inspect and verify.

To find the right level of constraint for a specific task, the first step is to choose the right **abstraction**. An abstraction hides low-level details and keeps only the concepts that actually matter. We then turn that abstraction into a **domain-specific language (DSL)**. You can think of a DSL as a small language designed for one kind of problem. It defines the vocabulary the AI can use, and the rules for how those pieces can be combined.

The DSL then becomes **a language for AI to think in and execute against**. Instead of reasoning over a huge space of arbitrary code and actions, the AI works with a smaller set of meaningful building blocks. These blocks can then be executed by a domain-specific runtime engine, whether that means SQL queries, statistical analysis, stateful event processing, or other specialized tools. The AI still has room to be creative in how it combines them, but its reasoning now stays within a space that humans can understand, check, and control.

### Two concrete examples of Constrained Creativity

We showcase how to build Constrained Creativity in two applications, and how it can improve accuracy while reducing cost.

**Root cause analysis.** In the RCA task, we represent troubleshooting as reusable building blocks, such as generating possible causes, comparing them against normal behavior, and ranking the evidence. The AI can only combine these blocks into a diagnosis workflow instead of writing arbitrary analysis code. If the existing blocks are not enough, it can create new ones while still following the same DSL. This gives the agent room to handle new incidents, but keeps every analysis structured and checkable.
<!-- TODO: cite LegoRCA (add to References). -->

<div class="figure figure-pair figure-card">
  <img src="{{ '/assets/img/posts/constrained-creativity/legorca-cc.png' | relative_url }}" alt="Root cause analysis via Constrained Creativity. The task “Why did login failures spike at 10am?” goes to a DSL or playbook of blocks such as find change point, filter and rank candidates; the LLM picks a playbook or composes a new DAG; the DSL program chains find_change_point, filter and rank_candidates; a runtime engine runs it with SQL, statistics and ML, iterating with the LLM; the answer ranks clients in region R as the top cause.">
  <div data-vega="/assets/data/constrained-creativity-rca-accuracy-cost.vl.json"></div>
</div>

<p class="figure-caption figure-caption-center"><strong>Fig. 3.</strong> In RCA, constrained creativity achieves higher diagnostic accuracy while reducing analysis cost by up to 12×.</p>

**Cybersecurity red-teaming.** Incalmo [[3]](#ref-3) follows the same idea for autonomous network attacks. Instead of letting an AI directly write low-level shell commands, it gives the agent higher-level actions such as *scan a network* or *infect a host*. Incalmo handles the messy low-level execution and keeps track of the network state. This lets the AI focus on deciding what to do next, rather than on how to implement every command correctly.

<div class="figure figure-pair figure-card">
  <img src="{{ '/assets/img/posts/constrained-creativity/incalmo-cc.png' | relative_url }}" alt="Cyber red-teaming via Constrained Creativity. The task “Gain access and exfiltrate sensitive data” goes to a DSL or playbook of actions such as scan, exploit and lateral move; the LLM plans a sequence of high-level attack actions; the DSL program runs Scan, LateralMove and ExfiltrateData; a runtime engine executes them with nmap, Metasploit and state tracking, iterating with the LLM; the answer is an attack path from foothold to pivot to finding data to exfiltration.">
  <div data-vega="/assets/data/open-weights-cost-vs-goals.vl.json"></div>
</div>

<p class="figure-caption figure-caption-center"><strong>Fig. 4.</strong> In cyber red-teaming, constrained creativity (the Incalmo harness) significantly improves attack success rate while reducing cost by more than 20×, compared with free-form AI agents.</p>

### How is Constrained Creativity different from X?

We have recently seen synergies between Constrained Creativity and many newly released AI tools and concepts. Let’s use the same RCA task as an example:

{% include modules/table.html data="cc-vs-x" class="table-soft table-compact" %}

**Constrained Creativity vs. Jev and decision APIs.** [Jev](https://docs.typesafe.ai/primitives) from TypeSafe AI [[4]](#ref-4) follows a very similar philosophy with a specific set of decision primitives. Jev’s output space is deliberately narrow: rather than asking the model to directly answer a complex question, it asks the model to make one typed decision. TypeSafe explicitly recommends decomposing complex decisions into atomic questions and composing their answers in code. OpenAI’s latest decision APIs propose similar ideas.
<!-- TODO: cite OpenAI decision APIs. -->

Constrained Creativity is broader than a particular set of decision primitives (e.g., a classification, a boolean, or a score). It can use different abstractions: for example, query telemetry, compare two time windows, generate a candidate hypothesis, validate a configuration, or execute a controlled system action. The answering structure can also extend beyond atomic questions: the AI can form a sequential chain, a parallel DAG, an iterative workflow, or a finite-state machine. The abstraction itself can also evolve as the task requirements change.

**Constrained Creativity vs. neuro-symbolic AI.** Neuro-symbolic AI also tries to combine the flexibility of neural models with explicit structure. The key idea is to connect neural learning or perception with symbolic knowledge and reasoning. For example, DeepProbLog [[5]](#ref-5) combines neural networks with probabilistic logic, while Neural Logic Machines [[6]](#ref-6) use neural networks to learn and execute logic-like rules.

Constrained Creativity has a different goal. It does not require the neural model and the symbolic reasoning system to be integrated or jointly learned. The LLM can remain a black box. Instead, Constrained Creativity puts domain knowledge around the agent to define the space in which it can act, while leaving the model free to reason within that space.

**Constrained Creativity vs. Structured LLM.** Researchers from UIUC proposed [Structured LLM](https://structuredllm.com/) [[7]](#ref-7), which shares a similar idea with Constrained Creativity. Their work focuses on making the model follow a given structure or grammar, such as valid JSON, code, or other structured outputs. This can make generation more reliable and easier for software to consume.

Constrained Creativity goes beyond constraining the format of the output. It constrains what actions the AI can take and how those actions can be combined. Structured LLM can be a concrete building block for Constrained Creativity at the decoding level, while Constrained Creativity designs the broader action space and workflow around the AI.

### What comes next for Constrained Creativity

Constraining AI is not automatically better. Too little freedom makes the agent rigid; too much brings us back to arbitrary code and difficult verification. We believe the key systems challenge is finding the right abstraction: expressive enough to handle new situations, but structured enough to understand, verify, and control.

We are actively bringing Constrained Creativity to more critical applications across networking, systems, and cybersecurity. **Our goal is simple: with the right constraints, we can unlock more of AI’s capability while making it cheaper, safer, and easier to trust. Stay tuned.**

### References

<ol class="references">
  <li id="ref-1"><em>Constrained Creativity for SysOps Agents.</em> Preprint, 2026. Sayan Sinha, Vipul Harsh, Yajie Zhou, Marko Morrison, B. Aditya Prakash, Vyas Sekar, Hui Zhang. <a href="https://kilthub.cmu.edu/articles/preprint/Constrained_Creativity_for_SysOps_Agents/33138296?file=67183613">[preprint]</a></li>
  <li id="ref-2"><em>What will be left for us to work on.</em> ICML 2026 keynote. Arvind Narayanan. <a href="https://www.cs.princeton.edu/~arvindn/talks/icml-2026-annotated-slides/">[slides]</a></li>
  <li id="ref-3"><em>Incalmo: An Autonomous LLM-Assisted System for Red Teaming Multi-Host Networks.</em> IEEE Symposium on Security and Privacy (S&amp;P), 2026. Brian Singer, Keane Lucas, Lakshmi Adiga, Meghna Jain, Lujo Bauer, Vyas Sekar. <a href="https://doi.org/10.1109/SP63933.2026.00132">[doi]</a></li>
  <li id="ref-4"><em>Jev primitives.</em> TypeSafe AI documentation. <a href="https://docs.typesafe.ai/primitives">[docs]</a></li>
  <li id="ref-5"><em>DeepProbLog: Neural Probabilistic Logic Programming.</em> NeurIPS, 2018. Robin Manhaeve, Sebastijan Dumančić, Angelika Kimmig, Thomas Demeester, Luc De Raedt. <a href="https://arxiv.org/abs/1805.10872">[arXiv]</a></li>
  <li id="ref-6"><em>Neural Logic Machines.</em> ICLR, 2019. Honghua Dong, Jiayuan Mao, Tian Lin, Chong Wang, Lihong Li, Denny Zhou. <a href="https://arxiv.org/abs/1904.11694">[arXiv]</a></li>
  <li id="ref-7"><em>Structured LLM.</em> UIUC. <a href="https://structuredllm.com/">[website]</a></li>
</ol>
