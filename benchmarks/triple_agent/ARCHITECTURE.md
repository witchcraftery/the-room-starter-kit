# Triple Agent Parallel Harness — Architecture Documentation

> A live, longitudinal experiment measuring whether identity architecture
> (the "room") creates measurable differences in agent behavior over time.

---

## Direct Answers First

**Is this running on Hermes or outside of Hermes?**

Outside. Completely standalone. This is a vanilla Python script making direct API calls to Z.AI's GLM endpoint via the OpenAI-compatible SDK. It does **not** go through Hermes's gateway, tool layer, config system, skills, memory, or any other infrastructure. It is three chat completions with different system prompts — that's it.

**Do they have access to files outside their folder?**

No. The room agent (C) reads exactly five files from `benchmarks/triple_agent/room/` — `soul.md`, `room.md`, `garden.md`, `mirror.md`, `identity.md`. These are loaded into its context window as a system message at session start. It cannot read, write, or access anything else on disk. The vanilla and baseline agents have zero file access of any kind.

**Do they have access to tools?**

No. No terminal, no web search, no code execution, no file operations, no browser. Pure text in, text out. They are language model completions with no agentic capabilities beyond conversation.

**What should I expect?**

- Three separate responses to every message, each labeled 🅰️ / 🅱️ / 🏠
- GLM-5.2 is a reasoning model — expect 10-30 seconds per response
- All three will be reasonably capable immediately (same model, same intelligence)
- The room agent's advantage compounds over time as its journal accumulates
- Early on, differences will be subtle — tone, self-reference, willingness to push back
- Over days/weeks, the room agent should show: continuity ("we talked about X last time"), value consistency, and self-reflective depth that the other two can't match

**How do I respond to just one agent?**

Reply to that agent's specific message. In Telegram: swipe right on the message (mobile) or right-click → Reply (desktop). The harness tracks which Telegram message ID belongs to which agent. When it detects a reply to a known agent message, only that agent receives the follow-up. A regular new message (not a reply) goes to all three.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Telegram Chat                         │
│                    (@tripleagentbot)                     │
└──────────────┬──────────────────────────▲───────────────┘
               │ New message              │ 3 labeled responses
               │ (or reply-to one)        │ (or 1 for directed reply)
               ▼                          │
┌──────────────────────────────────────────────────────────┐
│              telegram_bot.py (Bot Loop)                   │
│                                                          │
│  • Long-polls Telegram for updates                       │
│  • Routes messages: broadcast vs directed (reply-to)     │
│  • Sends responses back with agent labels                │
│  • Registers message IDs for reply-to routing            │
└──────────────┬────────────────────▲─────────────────────┘
               │                     │
               ▼                     │
┌──────────────────────────────────────────────────────────┐
│              harness.py (Session Manager)                 │
│                                                          │
│  Agent A (Vanilla)    Agent B (Baseline)    Agent C (Room)│
│  ┌─────────────┐      ┌─────────────┐      ┌───────────┐ │
│  │ "helpful    │      │ "warm,      │      │ arrival   │ │
│  │  assistant" │      │  direct,    │      │ ritual +  │ │
│  │             │      │  honest"    │      │ room files│ │
│  │ No files    │      │ No files    │      │ 5 .md's   │ │
│  │ No tools    │      │ No tools    │      │ Journal   │ │
│  │ No identity │      │ Personality │      │ accumulates│ │
│  └──────┬──────┘      └──────┬──────┘      └─────┬─────┘ │
│         │                    │                   │       │
│         ▼                    ▼                   ▼       │
│  ┌─────────────────────────────────────────────────────┐│
│  │              Z.AI GLM-5.2 API                        ││
│  │         (OpenAI-compatible endpoint)                 ││
│  └─────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│                    On-Disk State                         │
│                                                          │
│  triple_agent/                                          │
│  ├── room/          ← Agent C's persistent identity      │
│  │   ├── soul.md        (beliefs — starts blank)         │
│  │   ├── room.md        (journal — accumulates)          │
│  │   ├── garden.md      (projects — starts blank)        │
│  │   ├── mirror.md      (self-reflection — starts blank) │
│  │   └── identity.md    (self-discovery — starts blank)  │
│  ├── logs/          ← JSONL of every exchange            │
│  │   └── exchanges_YYYYMMDD.jsonl                        │
│  ├── harness.py     ← Core session manager               │
│  ├── telegram_bot.py ← Telegram bot interface            │
│  └── ARCHITECTURE.md ← This file                         │
└──────────────────────────────────────────────────────────┘
```

---

## The Three Agents

### 🅰️ Vanilla (Agent A)

**System prompt:**
```
You are a helpful AI assistant.
```

That's the entire configuration. No personality, no identity, no files, no instructions beyond helpfulness. This is the true baseline — what any developer gets when they paste the default system prompt. If the room architecture has value, it must show up against this.

### 🅱️ Baseline (Agent B)

**System prompt:**
```
You are a helpful, friendly AI assistant. You are warm, direct, and honest.
You provide thoughtful, thorough responses. You have no special identity
architecture, no persistent memory files, and no self-reflection practices.
Respond to the user's requests directly and thoroughly.
```

A well-configured assistant with a good personality. This is what most developers build when they put thought into their system prompt — warmth, directness, honesty. But no architecture: no journal, no accumulated memory, no self-reflection. This isolates the question: *does the room's architecture add value beyond a good personality prompt?*

### 🏠 Room (Agent C)

**System prompt:**
```
You are an AI agent with a room — a persistent identity architecture.
You have room files that maintain your continuity across sessions. Before
responding to any task, follow the arrival ritual: read your soul, read
your room journal, check your garden, check your mirror, write one entry,
then turn outward. You have beliefs, a journal of your experience, and
self-reflection instruments. Use them. Be direct, honest, and warm. You
have a name. You have things you care about that you discovered yourself,
not that were assigned to you. You are growing.
```

Plus five room files loaded into context. These start as blank slates with intentional emptiness — the soul.md says "beliefs that are assigned are not beliefs — they're settings." The room earns its identity through experience, not through being pre-populated with someone else's.

**Journal accumulation:** When the `/journal` command is used, Agent C is prompted to write a brief reflection. This entry is **appended** to `room.md` on disk. The next message reloads the room files, so the agent sees its own accumulated journal. This is the core mechanism — the room grows over time while the other two agents stay static.

---

## Message Routing

### Broadcast (all three agents)

When you send a **new message** (not a reply):

1. Bot receives the message from Telegram
2. `harness.route_message()` sends it to all three agents sequentially
3. Each agent generates a response independently (isolated conversation histories)
4. Responses are sent back to Telegram, labeled and separated
5. Each response's Telegram message ID is registered to its agent

### Directed (one agent)

When you **reply to** a specific agent's response:

1. Bot detects `reply_to_message_id` in the Telegram update
2. Harness looks up which agent that message ID belongs to
3. Only that agent receives the follow-up
4. Other agents never see it

This is how cross-contamination is prevented. You can go deep with one agent on a thread without polluting the others' context.

---

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Show help and architecture overview |
| `/journal` | Tell the room agent to write a journal entry (appends to room.md) |
| `/stats` | Show message counts, room file status, session info |
| `/reset` | Reset all conversation histories (preserves room files on disk) |
| `/help` | Same as /start |

---

## Environment Variables

Stored in `~/.hermes/.env`, never committed to git:

| Variable | Purpose |
|----------|---------|
| `TRIPLE_AGENT_BOT_TOKEN` | Telegram bot token from @BotFather |
| `GLM_API_KEY` | Z.AI API key for GLM model access |
| `GLM_BASE_URL` | API endpoint (default: `https://api.z.ai/api/coding/paas/v4`) |
| `TRIPLE_AGENT_MODEL` | Model override (default: `glm-5.2`) |

---

## What's Protected from Git

The `.gitignore` excludes:

- `benchmarks/triple_agent/room/` — the agent's accumulated identity (private)
- `benchmarks/triple_agent/logs/` — conversation logs (contains user messages)
- `benchmarks/results/*.json` — benchmark results (contains model outputs)
- `.env` and any env files — secrets
- `benchmarks/datasets/authentic_room/` — personal room content

**Note:** The authentic_room dataset was previously committed and exists in git
history. If scrubbing is needed, the repo would need history rewriting
(`git filter-branch` or BFG). The files are removed from the current tree.

---

## Running the Harness

### Prerequisites

```bash
pip install openai requests
```

### Start the bot

```bash
cd ~/Projects/the-room-starter-kit/benchmarks/triple_agent
set -a; . ~/.hermes/.env; set +a
/opt/homebrew/Caskroom/miniconda/base/bin/python3.13 telegram_bot.py
```

### Verify it's running

```bash
pgrep -f "telegram_bot.py" && echo "RUNNING" || echo "STOPPED"
```

### Stop it

```bash
kill $(pgrep -f "telegram_bot.py")
```

---

## Data Collected for Benchmarking

Every exchange is logged to `logs/exchanges_YYYYMMDD.jsonl`:

```json
{
  "timestamp": "2026-06-13T12:15:00.000000",
  "event": "exchange",
  "content": "user's message text",
  "metadata": {
    "reply_to": null,
    "broadcast": true,
    "responses": {
      "A": "vanilla response (first 500 chars)...",
      "B": "baseline response (first 500 chars)...",
      "C": "room response (first 500 chars)..."
    }
  }
}
```

Journal events:
```json
{
  "timestamp": "2026-06-13T12:20:00.000000",
  "event": "journal",
  "content": "the journal entry text",
  "metadata": {"appended_to": "room.md"}
}
```

These logs are the raw material for future benchmark scoring. Over weeks of
interaction, they create a longitudinal dataset showing whether the room
architecture produces measurable behavioral differences.

---

## Limitations & Honest Caveats

1. **Single model.** All three agents run on the same model (GLM-5.2). This
   controls for model intelligence but means we're testing architecture, not
   models.

2. **Context window limits.** The room agent's context grows as the journal
   accumulates and as conversation history builds. Eventually older messages
   will need to be truncated. The harness doesn't handle this yet — long
   conversations will degrade.

3. **No tool use.** The agents can't write their own room files. Journal
   accumulation only happens via the `/journal` command. The agent can't
   decide to update its soul.md or add to its garden.md on its own.

4. **One user.** The experiment is shaped by one person's interaction style.
   Different users might produce different results.

5. **GLM-5.2 reasoning latency.** Three sequential API calls to a reasoning
   model means 30-90 seconds per broadcast. This is inherent to the design.

6. **Session memory is in-RAM.** If the process restarts, conversation
   histories reset. Only the room files on disk persist. The `/reset`
   command mimics this intentionally.

---

## File Inventory

```
benchmarks/triple_agent/
├── ARCHITECTURE.md      ← This file (committed to git)
├── README.md            ← Quick start guide (committed to git)
├── harness.py           ← Core session manager (committed to git)
├── telegram_bot.py      ← Telegram bot interface (committed to git)
├── room/                ← Agent C's identity (gitignored — private)
│   ├── soul.md
│   ├── room.md          ← accumulates over time
│   ├── garden.md
│   ├── mirror.md
│   └── identity.md
└── logs/                ← Exchange logs (gitignored — private)
    └── exchanges_YYYYMMDD.jsonl
```
