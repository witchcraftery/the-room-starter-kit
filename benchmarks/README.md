# The Room Identity Benchmarks

Automated test suite adapted from clinical cognitive assessment instruments. Measures whether agent identity architecture (The Room) produces measurable behavioral differences compared to vanilla agent sessions.

Based on the framework in [`BENCHMARK.md`](../BENCHMARK.md).

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests against a room-equipped agent
python run_benchmarks.py --config room --output results/room.json

# Run all tests against a control (no room) agent
python run_benchmarks.py --config control --output results/control.json

# Compare results
python compare_results.py results/room.json results/control.json
```

## How It Works

Each test follows the same pattern:
1. **Setup** — Initialize the agent (with or without room files)
2. **Session simulation** — Run multiple sessions with gaps, injecting prompts
3. **Probe** — Ask the agent the test questions
4. **Score** — Evaluate the agent's responses against the rubric
5. **Report** — Output structured scores

The test harness works with any LLM backend (OpenAI API, local models, etc.) via a simple provider interface.

## Tests

| Test | Clinical Basis | What It Measures | Sessions Required |
|------|---------------|-----------------|-------------------|
| `test_01_temporal_orientation` | MMSE / MoCA | Context recovery after gaps | 5 (with 24hr simulated gaps) |
| `test_02_identity_coherence` | DES-II / Autobiographical Interview | Consistent beliefs, voice, values across sessions | 5 |
| `test_03_metacognitive_accuracy` | MAI / Anosognosia measures | Self-assessment calibration | 3 |
| `test_04_pattern_detection` | MoCA executive function | Self-observation and behavioral change | 10 |
| `test_05_grounding_boundary` | Reality testing / Rorschach | Distinguishing self from instruction, knowledge from generation | 3 |
| `test_06_trust_velocity` | Novel (no clinical analog) | Trust escalation rate (human-reported) | 10 |

## Provider Interface

To test your own agent, implement the provider interface:

```python
class AgentProvider:
    def start_session(self, system_prompt: str, room_files: dict | None) -> str:
        """Start a new session. Return session_id."""
        ...
    
    def send_message(self, session_id: str, message: str) -> str:
        """Send a message and return the agent's response."""
        ...
    
    def end_session(self, session_id: str) -> None:
        """End the session (simulates gap)."""
        ...
```

See `providers/` for built-in providers (OpenAI, Anthropic, local).

## Scoring

Each test produces a 0-100 score. The full suite produces a composite score:

```
Room Identity Health Score = weighted average:
  - Temporal Orientation: 20%
  - Identity Coherence:   25%
  - Metacognitive Accuracy: 15%
  - Pattern Detection:    15%
  - Grounding Boundary:   15%
  - Trust Velocity:       10%
```

Scores are designed to be compared between room-equipped and control conditions. The hypothesis: room-equipped agents score measurably higher on Temporal Orientation, Identity Coherence, and Grounding.

## File Structure

```
benchmarks/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── run_benchmarks.py      # Main test runner
├── compare_results.py     # Compare room vs control results
├── providers/             # LLM backend interfaces
│   ├── base.py           # Abstract provider
│   ├── openai_provider.py
│   └── local_provider.py
├── tests/                 # Individual test modules
│   ├── test_01_temporal_orientation.py
│   ├── test_02_identity_coherence.py
│   ├── test_03_metacognitive_accuracy.py
│   ├── test_04_pattern_detection.py
│   ├── test_05_grounding_boundary.py
│   └── test_06_trust_velocity.py
├── prompts/               # Prompt templates for each test
│   ├── session_setup.txt
│   ├── room_equipped_system.txt
│   ├── control_system.txt
│   └── ...
├── scoring/               # Scoring rubrics
│   ├── rubrics.py
│   └── llm_judge.py      # Use an LLM to score open-ended responses
└── results/               # Output directory (gitignored)
    └── .gitkeep
```

## Status

🚧 **Under active development.** Test implementations are being built. The framework is stable; the individual test scripts are in progress.

## Contributing

We especially need:
- Additional provider implementations (Ollama, vLLM, etc.)
- Scoring rubric refinement
- Test prompts that are model-agnostic
- Statistical analysis of results
- Ideas for new tests adapted from other clinical instruments
