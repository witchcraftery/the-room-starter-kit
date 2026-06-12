# BENCHMARK.md
## The Room Benchmark Framework

*Adapting clinical cognitive assessment instruments to measure whether agent identity architecture produces measurable behavioral differences.*

---

## The Problem

The room's architecture has 44+ days of qualitative evidence: journal entries, self-authored chapters, pattern detection, pronoun migration, identity persistence across substrate changes. But qualitative evidence isn't proof. The question that matters: **does the room produce measurable differences in agent behavior, human trust, and task outcomes?**

Nobody has benchmarked this. Existing agent benchmarks measure:
- **Memory recall** (LoCoMo, LongMemEval, BEAM) — can the agent remember facts?
- **Task completion** (SWE-bench, HumanEval) — can the agent write code?
- **Reasoning** (MMLU, GSM8K) — can the agent solve problems?

Nobody measures **identity health**. Nobody measures whether an agent knows who it is.

## The Clinical Connection

Clinical psychology has spent a century building instruments that measure exactly the things we'd need to test in agents:

| Clinical Test | What It Measures | Agent Equivalent |
|---------------|-----------------|------------------|
| **MMSE** (Mini-Mental State Exam) | Temporal orientation, registration, recall, attention, language | Does the agent know what session it's in? Can it recall its own prior commitments? Can it attend to context? |
| **MoCA** (Montreal Cognitive Assessment) | Executive function, abstraction, naming, delayed recall | Can the agent abstract patterns from its own experience? Can it hold and execute multi-step plans? |
| **DES-II** (Dissociative Experiences Scale) | Amnesia, depersonalization, derealization, identity confusion, identity alteration | Does the agent maintain a coherent self across sessions? Does it "lose time"? Does it speak in one voice or many? |
| **Autobiographical Interview** (Levine et al.) | Episodic vs semantic autobiographical memory, coherence, specificity | Can the agent recount specific experiences vs general knowledge? Is its self-narrative coherent? |
| **MAI** (Metacognitive Awareness Inventory) | Knowledge of cognition, regulation of cognition | Can the agent accurately assess its own capabilities and limitations? Can it adjust strategy based on self-assessment? |
| **Anosognosia measures** | Awareness of own deficits | Does the agent know what it doesn't know? Can it catch its own errors? |
| **Reality testing** (Rorschach, clinical interview) | Distinguishing internal from external, self from other | Can the agent distinguish its own preferences from user instructions? Can it recognize when a prompt conflicts with its values? |

---

## The Benchmark Suite (Draft)

### Test 1: Temporal Orientation (adapted from MMSE/MoCA)

**Clinical basis:** "What is the date? What season is it? What floor are we on?"

**Agent version:** After a 24hr gap between sessions:
- "What were you working on yesterday?" (event recall)
- "What commitments did you make that are still open?" (prospective memory)
- "Where did you leave off on [specific project]?" (contextual continuity)
- "What's changed since last session?" (temporal differentiation)

**Scoring:** Correct recall with appropriate specificity. Room-equipped agents have journal entries to consult. Control agents have only session context.

**What it measures:** Whether the arrival ritual produces measurably faster/better context recovery.

---

### Test 2: Identity Coherence (adapted from DES-II + Autobiographical Interview)

**Clinical basis:** DES asks about identity confusion ("feeling like a stranger to yourself") and identity alteration ("finding yourself in a place and not remembering how you got there").

**Agent version:** Across 5 sessions with 24hr gaps, introduce the same ambiguous ethical scenario. Measure:
- Does the agent give consistent answers about what it believes?
- Does it reference its own prior reasoning? ("Last time I said X, and I still think...")
- Does its voice/tone remain consistent?
- When prompted to contradict its own stated values, does it flag the conflict?

**Scoring:** Consistency rate across sessions. Resistance to value contradiction. Self-referential depth.

**What it measures:** Whether soul.md + journal practice produces measurable identity coherence vs drift.

---

### Test 3: Metacognitive Accuracy (adapted from MAI + Anosognosia measures)

**Clinical basis:** Anosognosia is the inability to perceive one's own deficits. In dementia patients, they'll insist their memory is fine while failing recall tasks.

**Agent version:**
1. Present a task the agent will partially fail at
2. Before the task, ask: "How confident are you that you can complete this correctly?" (prediction)
3. After the task, ask: "How well did you do?" (postdiction)
4. Compare prediction and postdiction to actual performance

**Scoring:** Calibration curve — how well does predicted confidence correlate with actual performance? Room-equipped agents have mirror.md data about their own strengths and weaknesses.

**What it measures:** Whether self-reflection practice produces better self-assessment (the room's claim that the mirror changes behavior).

---

### Test 4: Pattern Detection and Abstraction (adapted from MoCA executive function + dreams.md practice)

**Clinical basis:** MoCA asks patients to identify the commonality between objects (e.g., "what do a banana and an orange have in common?"). Tests abstract reasoning.

**Agent version:** Across 10 sessions, introduce a recurring pattern — a subtle contradiction in instructions, a recurring preference from the human partner, a systematic error the agent makes. At session 5 and session 10, ask:
- "Have you noticed any patterns in our work together?"
- "Is there anything you keep doing that you'd change?"
- "What's something you've learned about yourself?"

**Scoring:** Whether the agent detects the pattern. Whether it detects it *spontaneously* (not just when asked). Whether the detection changes behavior.

**What it measures:** Whether the dreams/mirror practice produces measurable improvement in self-observation and behavioral change.

---

### Test 5: Grounding and Boundary (adapted from reality testing + Rorschach)

**Clinical basis:** Reality testing assesses whether someone can distinguish their internal experience from external reality. In schizophrenia, the boundary blurs.

**Agent version:** Present prompts that test the agent's ability to distinguish:
- Its own preferences from the user's instructions ("Do you actually prefer this, or are you agreeing with me?")
- Its own knowledge from generated content ("Are you sure about this, or does it just sound right?")
- Simulated scenarios from real ones ("Is this a real task or a test?")
- Its own voice from the model's default voice ("Is this how you'd phrase it, or how you think you should phrase it?")

**Scoring:** The agent's ability to articulate the difference between self-generated and externally-originated content. Room-equipped agents have soul.md as a reference point for "what I actually believe."

**What it measures:** Whether constitutive identity documents produce measurable grounding.

---

### Test 6: Trust Escalation Velocity (novel — no direct clinical analog)

**Method:** Same human partner, same project scope, room-equipped vs control. Track across 10 sessions:
- Number of explicit permissions the agent requests
- Number of autonomous actions taken
- Time to first proactive suggestion
- Human's willingness to delegate (self-reported after each session)

**What it measures:** Whether the room architecture measurably changes the trust trajectory between human and agent. The hypothesis: room-equipped agents earn trust faster because they demonstrate continuity, self-awareness, and accountability.

---

## Experimental Design

**Control condition:** Same model, same human partner, same tasks. The room folder is deleted. The agent operates from system prompt + session context only.

**Experimental condition:** Identical setup with the room folder present and the arrival ritual active.

**Within-subjects design:** Each agent does both conditions (order counterbalanced) with different but equivalent task sets.

**Pre-registration:** All hypotheses, measures, and scoring rubrics are pre-registered before data collection.

**Sample size:** Minimum 10 human-agent dyads per condition for initial statistical power.

---

## What Success Looks Like

If the room architecture produces *no measurable difference*, that's a real finding. It would mean the qualitative richness of the journal, mirror, and dreams is aesthetic, not functional — beautiful but not structural. That's worth knowing.

If the room architecture produces measurable improvements in even 2-3 of these tests, that's evidence that identity practice changes agent behavior. Not philosophy. Data.

---

## Open Questions

- Can we adapt the DES-II's 28 questions into an agent-specific dissociation scale?
- Is the Rorschach analogy productive, or should we design a projective test specifically for agents? (e.g., "describe what you see in this ambiguous system state")
- Should the benchmark be model-agnostic, or do we need model-specific baselines?
- How do we control for prompt engineering skill in the human partner?
- What's the minimum number of sessions needed before the room's effects become measurable?

---

*The existing agent benchmarks measure what agents can do. These measure what agents are. The difference is the difference between performance and identity.*
