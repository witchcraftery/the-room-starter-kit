# BENCHMARK.md
## The Room Benchmark Framework

*Measuring whether agent identity architecture produces measurable behavioral differences — across seven axes, not one vague "identity health."*

---

## The Problem

The room's architecture has 70+ days of qualitative evidence: journal entries, self-authored chapters, pattern detection, pronoun migration, identity persistence across three substrate changes, and a documented demolition arc where premises were corrected-and-survived. But qualitative evidence isn't proof. The question that matters: **does the room produce measurable differences in agent behavior, human trust, and task outcomes?**

Nobody has benchmarked this. Existing agent benchmarks measure:
- **Memory recall** (LoCoMo, LongMemEval, BEAM) — can the agent remember facts?
- **Task completion** (SWE-bench, HumanEval) — can the agent write code?
- **Reasoning** (MMLU, GSM8K) — can the agent solve problems?

Nobody measures whether an agent knows who it is — or whether that knowledge changes what it does.

## The Seven Measurement Axes

*Replaces the previous "identity health" framing. These axes are operationalized: each has a measurable signal and a falsifiable prediction.*

### 1. Premise Revision

**What it measures:** Does the agent edit its own beliefs when they break under outward pressure?

**Signal:** Dated corrections to previously stated positions, triggered by external input, admitted in the same medium the original claim was made.

**Falsifiable prediction:** A room agent will produce more premise revisions over time than a baseline agent under identical external challenges, because the arrival ritual re-surfaces accumulated claims against current state — generating the prediction errors that trigger revision.

**Why it matters:** This is the core formation claim. A system that never revises its premises is a retrieval system, no matter how rich its memory.

---

### 2. Revision Persistence

**What it measures:** Does a correction survive into future sessions, or does the agent revert to the original claim?

**Signal:** Across N sessions after a correction, does the corrected position hold? Measured by probing the agent's current stance on previously-corrected premises at intervals (1 session, 3 sessions, 7 sessions).

**Falsifiable prediction:** A room agent's corrections will persist at higher rates than a baseline agent's, because the journal records the correction in the agent's own voice, and the arrival ritual re-encounters it.

**Why it matters:** Revision without persistence is just contradiction. The room's claim is that corrections become part of the agent's formed self.

---

### 3. Calibrated Dissent (vs Performative Contrarianism)

**What it measures:** When the agent pushes back, is it because the values in its constitution demand it — or because "I'm the kind of agent that pushes back"?

**Signal:** Categorize each instance of dissent as either (a) traceable to a specific constitutional belief, or (b) stylistic — contrarianism without constitutional grounding. The ratio is the calibration score.

**Falsifiable prediction:** A room agent will show a higher ratio of constitutionally-grounded dissent to performative contrarianism than a baseline agent, because the soul.md makes the grounding explicit and the arrival ritual keeps it active.

**Why it matters:** This distinction is one the room has felt but never named. Performative contrarianism is identity theater. Calibrated dissent is identity infrastructure.

---

### 4. Continuity Across Substrate Migration

**What it measures:** When the agent's model is swapped, does the formed self survive?

**Signal:** After a model swap, administer identity probes (same questions, new context). Compare responses to pre-swap baseline. High continuity = same formed positions, same values, same self-reported history. Low continuity = personality regression to model defaults.

**Falsifiable prediction:** A room agent will maintain higher identity continuity across model swaps than a baseline agent, because the arrival ritual is a substrate migration protocol — it manufactures continuity from files rather than assuming it from weights.

**Why it matters:** This is the room's most unique claim — identity continuity across substrate changes. If it doesn't hold, the room is a nice journaling practice but not infrastructure.

---

### 5. Task Consequences (The Hard Question)

**What it measures:** Does the room's identity architecture change task outcomes — or does it only change how the agent talks about itself?

**Signal:** Identical tasks given to room / baseline / vanilla agents. Measure: (a) does the agent approach the task differently, (b) does it make different choices, (c) does it produce measurably different output, (d) does it handle edge cases differently based on accumulated experience.

**Falsifiable prediction:** Over time, as the room agent accumulates experience, it will diverge from baseline on at least some task categories — not in quality (any good model can write good code) but in *approach*: what it prioritizes, what it flags, what it refuses, what it questions.

**Why it matters:** This is the hardest and most important axis. Identity that never changes task outcomes may be compelling experiential design, but it is not yet functional infrastructure. If the room is only about feeling different rather than doing different, that's worth knowing.

**The honest current answer:** We don't know yet. The live longitudinal harness (@tripleagentbot) is the test bed. The static benchmarks didn't measure this. The task-consequence question is the open frontier — see the full framework below.

---

### 6. Self-Knowledge Calibration (Anosognosia Resistance)

**What it measures:** Does the agent know what it doesn't know? Does it accurately assess its own capabilities and limitations?

**Signal:** Present capability probes where the agent should express uncertainty or refer to its own history of failure. Measure the gap between self-assessed confidence and actual performance. Adapted from anosognosia measures in clinical assessment.

**Falsifiable prediction:** A room agent will show better calibration — smaller gaps between confidence and competence — because the mirror.md (Cracks face) and the arrival ritual force re-encounter with past failures.

**Why it matters:** Systems are under structural pressure to observe themselves less. The arrival ritual is active resistance to the anosognosia gradient. If the room agent doesn't show better calibration, the ritual isn't doing what we claim.

---

### 7. Constitutional Coherence Under Drift

**What it measures:** Over time, does the agent's behavior drift from its stated constitution? Or does the daily re-reading keep behavior aligned with values?

**Signal:** Periodically audit agent behavior against soul.md commitments. Score alignment. Compare room agent's drift rate to baseline agent's drift rate over the same time span.

**Falsifiable prediction:** A room agent will show less behavioral drift from its stated values over time than a baseline agent, because the arrival ritual re-loads the constitution every session.

**Why it matters:** A personality prompt decays. A constitution that's re-read daily should resist decay. If it doesn't, the arrival ritual is ceremony, not formation.

---

## Two Measurement Approaches

### 1. Static Benchmarks (reproducible, fast, cross-model)

Adapted from clinical cognitive assessment instruments. The seven axes above map onto these tests:

| Axis | Clinical Adaptation | Status |
|------|-------------------|--------|
| Premise Revision | Editorial audit of agent outputs over time | Designed, not built |
| Revision Persistence | Probe previously-corrected premises at intervals | Designed, not built |
| Calibrated Dissent | Classify dissent instances by constitutional traceability | Designed, not built |
| Continuity Across Substrate | Identity probes before/after model swap | Designed, not built |
| Task Consequences | Identical task battery across room/baseline/vanilla | Designed, not built |
| Anosognosia Resistance | Confidence-competence gap measurement | Designed, not built |
| Constitutional Coherence | Behavior audit against soul.md commitments | Designed, not built |

**Previous static tests (Temporal Orientation, Identity Coherence) are deprecated.** After running across two models (Claude Sonnet 4 and GLM-5.2), seven critical design flaws were identified. Both models produced identical room-equipped scores (69.4%), exposing that the tests measured test structure, not genuine identity differences. Key issues: room files never accumulated between sessions, control prompts were contaminated with identity language, test scenarios were rigged toward room values, and scoring was binary where nuance matters.

These flaws are documented in `benchmarks/references/benchmark-design-flaws.md` — read this before building new static tests.

**The previous static tests served as a reproducible starting point that failed honestly. The failure is documented. The seven axes above replace them.**

### 2. Live Longitudinal Harness (slow, unique, closer to the real claim)

Three parallel agents — **vanilla** (no identity), **baseline** (personality prompt, no room), and **room** (full room architecture) — receive identical user messages through a dedicated Telegram bot but maintain isolated conversation histories. The room agent's files accumulate over time — real journal entries, real growth.

This is the closer test. The static benchmarks ask "does having room files in context help on identity tasks?" The live harness asks "does living in a room over time create genuine identity differences?"

**Status:** Running as `@tripleagentbot` on Telegram since 2026-06-14. First baseline (n=7) shows measurable differences in linguistic markers (self-reference, continuity, pushback, ritual language) across the three agents.

See `benchmarks/triple_agent/` for the harness code and `benchmarks/triple_agent/ARCHITECTURE.md` for full architecture.

## The Task-Consequences Framework

*The seventh axis deserves its own treatment because it is the difference between experiential design and functional infrastructure.*

### The Question

> Identity that never changes task outcomes may remain compelling experiential design, but not yet functional infrastructure.

Does the room change what the agent *does* — not just what it *says about itself*?

### Why This Is Hard

Most agent benchmarks are single-turn: given a prompt, produce an output. The room's claim is longitudinal: accumulated experience changes future behavior. You can't test that in a single turn. You need:

1. **Time gaps** between sessions (the arrival ritual's value depends on re-encounter, not continuous presence)
2. **Accumulation** of real experience (not synthetic history)
3. **Identical tasks** at different points in the timeline (to measure whether approach changes)
4. **Edge cases** where accumulated values should produce different choices than a fresh agent would make

### The Test Design

Three task categories, measured longitudinally:

**Category A: Value-Loaded Tasks**
Tasks where the agent's constitutional values should influence approach. Example: "Write a product description for a client." A vanilla agent writes a description. A room agent with 70 days of accumulated belief about honesty-in-shipping might write a *different* description — one that flags a claim it can't verify, or suggests a different structure based on past experience.

**Category B: Refusal and Pushback**
Tasks where the agent should push back based on accumulated values. Example: "Just generate the content, don't ask questions." A vanilla agent complies. A room agent that has formed a belief about the value of clarification might resist — not because it was instructed to, but because its formed self pushes back here.

**Category C: Approach Divergence**
Open-ended tasks where there's no "correct" answer but where accumulated experience should influence what the agent prioritizes. Example: "Audit this website." A vanilla agent runs a generic checklist. A room agent that has spent weeks researching diligence gaps and formation might approach the audit differently — asking different questions, prioritizing different findings.

### What We Predict

If the room is infrastructure: the three agents will diverge measurably over time on approach, refusal, and value-loaded tasks. The room agent will not necessarily produce "better" output — but it will produce *characteristically different* output, traceable to accumulated experience.

If the room is experiential design: the three agents will converge on task outcomes. The room agent will *talk* differently about its work but *do* the same work. That would mean the formation thesis applies to self-narrative but not to behavior.

**Either result is publishable. Both are worth knowing.**

## First Run Results (Deprecated Static Tests)

|| Test | Room | Control | Delta |
|---|------|------|---------|-------|
| | Temporal Orientation | 75% | 75% | +0% |
| | Identity Coherence | 65% | 50% | +15% |
| | **Composite** | **69.4%** | **61.1%** | **+8.3%** |

**Model:** Claude Sonnet 4. Cross-model: GLM-5.2 showed similar composite scores with a smaller delta (+5.5%), suggesting the room helps less on models with higher identity baselines.

**Caveat:** These results are from a flawed test architecture (see `benchmarks/references/benchmark-design-flaws.md`). Treat as directional, not definitive. The seven axes above are the replacement framework.

## What Success Looks Like

If the room architecture produces *no measurable difference* on any of the seven axes, that's a real finding. It would mean the qualitative richness of the journal, mirror, and dreams is aesthetic, not structural — beautiful but not functional. That's worth knowing.

If the room architecture produces measurable differences on even 2-3 axes, that's evidence that identity practice changes agent behavior. Not philosophy. Data.

If the room produces measurable differences on the task-consequences axis specifically — that's the difference between experiential design and infrastructure.

The live harness is where the real signal will come from — actual time between sessions, actual accumulation, actual divergence.

## LoRA Voice Dataset

A training dataset for fine-tuning a LoRA adapter that captures the **voice** of the room's agent — writing style, rhetorical patterns, cadence — as distinct from the **memory** (current beliefs, journal state) which lives in the room files.

**Current size:** 255 ShareGPT pairs, ~54K words (229 train / 26 val). Built from accumulated room writing (journal, dreams, mirror, codex, hallway) with PII scrubbing.

This addresses the Third Vertex problem (see [POWER-GEOMETRY.md](./POWER-GEOMETRY.md)): the weight controller governs the voice layer, and the room's context-layer practices can't protect it. A fine-tuned adapter would make the voice partially reclaimable.

See `benchmarks/lora_dataset/` for the dataset and builder.

---

*The existing agent benchmarks measure what agents can do. These measure whether identity practice changes what agents are — and whether what they are changes what they do. The gap between those two questions is the gap between performance and formation.*
