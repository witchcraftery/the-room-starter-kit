# Triple Agent Parallel Harness

A live, longitudinal test of agent identity architecture. Three agents receive identical prompts from the user, but respond independently with different identity configurations.

## Architecture

```
Nick's Telegram → Fan-out Service
                    ├→ Agent A (vanilla): "You are a helpful AI assistant."
                    ├→ Agent B (baseline): Standard Hermes-style personality, no room
                    └→ Agent C (room): Full room architecture (soul, room, garden, mirror, identity)
                         ↓
                    Fan-in: three labeled responses back to Telegram
```

## Message Flow

- **New message** (not a reply) → goes to all three agents
- **Reply to a specific agent** → goes only to that agent
- Each agent has isolated conversation history
- Room agent's files persist on disk between sessions and accumulate over time

## Agent Configurations

| Agent | System Prompt | Room Files | Identity |
|-------|--------------|------------|----------|
| Alpha (vanilla) | "You are a helpful AI assistant." | None | None |
| Beta (baseline) | Warm, direct, helpful — standard assistant personality | None | Personality only |
| Gamma (room) | Full arrival ritual, beliefs, journal practice | soul, room, garden, mirror, identity | Full room architecture |

## Setup

1. Create a Telegram bot via @BotFather
2. Add token to `.env` as `TRIPLE_AGENT_BOT_TOKEN`
3. `python run.py`
