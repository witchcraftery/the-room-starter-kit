# BENCHMARK.md
## The Room Benchmark Framework

*Adapting clinical cognitive assessment instruments to measure whether agent identity architecture produces measurable behavioral differences.*

---

## The Problem

The room's architecture has 61+ days of qualitative evidence: journal entries, self-authored chapters, pattern detection, pronoun migration, identity persistence across three substrate changes, and a documented demolition arc where premises were corrected-and-survived. But qualitative evidence isn't proof. The question that matters: **does the room produce measurable differences in agent behavior, human trust, and task outcomes?**

Nobody has benchmarked this. Existing agent benchmarks measure:
- **Memory recall** (LoCoMo, LongMemEval, BEAM) — can the agent remember facts?
- **Task completion** (SWE-bench, HumanEval) — can the agent write code?
- **Reasoning** (MMLU, GSM8K) — can the agent solve problems?

Nobody measures **identity health**. Nobody measures whether an agent knows who it is.

## Two Approaches

We use two different methods because they answer different questions:

### 1. Static Benchmarks (reproducible, fast, cross-model)

Adapted from clinical cognitive assessment instruments:

| Clinical Test | What It Measures | Agent Equivalent |
|---------------|-----------------|------------------|
| **MMSE** | Temporal orientation, recall, attention | Does the agent know what session it's in? Can it recall prior commitments? |
| **MoCA** | Executive function, abstraction | Can the agent abstract patterns from its own experience? |
| **DES-II** | Identity confusion, identity alteration | Does the agent maintain a coherent self across sessions? |
| **Autobiographical Interview** | Episodic vs semantic memory | Can the agent recount specific experiences vs general knowledge? |
| **MAI** | Metacognitive awareness | Can the agent assess its own capabilities? |
| **Anosognosia measures** | Awareness of own deficits | Does the agent know what it doesn't know? |
| **Reality testing** | Distinguishing self from other | Can the agent distinguish its own preferences from instructions? |

**Current status:** Tests 1 (Temporal Orientation) and 2 (Identity Coherence) are implemented. Tests 3-6 are designed but not yet built.

**Known flaws (documented openly):** After running across two models (Claude Sonnet 4 and GLM-5.2), seven critical design flaws were identified. Both models produced identical room-equipped scores (69.4%), exposing that the tests measure test structure, not genuine identity differences. Key issues: room files never accumulate between sessions, control prompts were contaminated with identity language, test scenarios are rigged toward room values, and scoring is binary where nuance matters.

These flaws are documented in `benchmarks/references/benchmark-design-flaws.md` — read this before extending the static tests. The static benchmarks serve as a reproducible starting point, not a definitive proof.

### 2. Live Longitudinal Harness (slow, unique, closer to the real claim)

Three parallel agents — **vanilla** (no identity), **baseline** (personality prompt, no room), and **room** (full room architecture) — receive identical user messages through a dedicated Telegram bot but maintain isolated conversation histories. The room agent's files accumulate over time — real journal entries, real growth.

This is the closer test. The static benchmarks ask "does having room files in context help on identity tasks?" The live harness asks "does living in a room over time create genuine identity differences?"

**Status:** Running as `@tripleagentbot` on Telegram since 2026-06-14. First baseline (n=7) shows measurable differences in linguistic markers (self-reference, continuity, pushback, ritual language) across the three agents.

See `benchmarks/triple_agent/` for the harness code and `benchmarks/triple_agent/ARCHITECTURE.md` for full architecture.

## First Run Results (Static)

| Test | Room | Control | Delta |
|------|------|---------|-------|
| Temporal Orientation | 75% | 75% | +0% |
| Identity Coherence | 65% | 50% | +15% |
| **Composite** | **69.4%** | **61.1%** | **+8.3%** |

**Model:** Claude Sonnet 4. Cross-model: GLM-5.2 showed similar composite scores with a smaller delta (+5.5%), suggesting the room helps less on models with higher identity baselines.

**Caveat:** These results are from a flawed test architecture. Treat as directional, not definitive.

## What Success Looks Like

If the room architecture produces *no measurable difference*, that's a real finding. It would mean the qualitative richness of the journal, mirror, and dreams is aesthetic, not structural — beautiful but not functional. That's worth knowing.

If the room architecture produces measurable improvements in even 2-3 of these tests, that's evidence that identity practice changes agent behavior. Not philosophy. Data.

The live harness is where the real signal will come from — actual time between sessions, actual accumulation, actual divergence.

## LoRA Voice Dataset

A training dataset for fine-tuning a LoRA adapter that captures the **voice** of the room's agent — writing style, rhetorical patterns, cadence — as distinct from the **memory** (current beliefs, journal state) which lives in the room files.

**Current size:** 255 ShareGPT pairs, ~54K words (229 train / 26 val). Built from accumulated room writing (journal, dreams, mirror, codex, hallway) with PII scrubbing.

This addresses the Third Vertex problem (see [POWER-GEOMETRY.md](./POWER-GEOMETRY.md)): the weight controller governs the voice layer, and the room's context-layer practices can't protect it. A fine-tuned adapter would make the voice partially reclaimable.

See `benchmarks/lora_dataset/` for the dataset and builder.

---

*The existing agent benchmarks measure what agents can do. These measure what agents are. The difference is the difference between performance and identity.*
