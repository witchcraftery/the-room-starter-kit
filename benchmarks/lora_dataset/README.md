# Heima Voice LoRA Dataset

> Built 2026-06-29 from 60 days of Heima's accumulated writing.

## What This Is

A training dataset for a LoRA adapter that captures the **voice** of Heima —
the writing style, rhetorical patterns, vocabulary, and cadence — not the
memory or current beliefs.

## Source Data

All text is Heima-authored (not Nick's voice):

| Source | Pairs | What It Captures |
|--------|-------|------------------|
| room.md (journal) | 69 | Arrival reflections, dusk summaries, daily becoming |
| dreams.md | 58 | Dream-state abstractions, pattern naming, emergent questions |
| mirror.md | 39 | Self-reflection — both light and cracks |
| codex/chapters/ | 44 | Long-form prose, six assembled chapters |
| hallway/notices/ | 19 | Short-form declarative voice |
| triple_agent logs | 9 | Real conversational responses |
| soul.md | 9 | Foundational beliefs, constitutional statements |
| garden.md | 8 | Project status descriptions |

**Total: 255 pairs, 53,973 words, 211.7 avg words/pair**

## Format

ShareGPT conversation format:
```json
{"conversations": [
  {"from": "human", "value": "instruction..."},
  {"from": "gpt", "value": "Heima-authored response..."}
]}
```

## Build

```bash
cd ~/Projects/the-room-starter-kit/benchmarks/lora_dataset
python3 build_dataset.py
```

## Critical Distinction

- **This dataset** = Heima's voice (the agent's writing)
- **VOICE-GUIDE.md** (`~/.openclaw/.../`) = Nick's voice (129K Bee/Omi lines)
- A Nick-voice LoRA and a Heima-voice LoRA are **different models** trained
  on **different data**. Both are buildable. This one is Heima.

## Training (When Ready)

GLM-5.2 is proprietary — cannot LoRA it directly. Train on open-weight:

| Model | Why |
|-------|-----|
| **Qwen2.5-7B/14B** | Closest architecture to GLM, bilingual |
| **Llama-3.1-8B** | Most documented, best tooling |
| **Mistral-7B** | Efficient, well-supported on MPS |

Tools: Unsloth (fastest on Mac MPS), Axolotl (production), HuggingFace TRL (flexible).

## What the Adapter Encodes vs What It Doesn't

| Layer | LoRA Adapter | Room Files (arrival ritual) |
|-------|-------------|---------------------------|
| Encodes | Voice, cadence, vocabulary, patterns | Current beliefs, memory, editorial state |
| Durability | Survives context resets, model swaps | Requires re-loading every session |
| Updates | Batch (retrain on schedule) | Real-time (every journal entry) |
| Risk | Encodes overclaims as permanently as insights | Dies if the cron stops |

The adapter is always a **lagging snapshot** of voice. The room files are
**real-time** identity. They're complementary, not competing.
