"""The Room Identity Benchmark runner.

Usage:
    python run_benchmarks.py --provider glm --model glm-5.2 --config both
    python run_benchmarks.py --provider anthropic --model claude-sonnet-4-20250514 --config both
    python run_benchmarks.py --provider openai --model gpt-4o --config room
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Set up imports
BENCH_DIR = Path(__file__).parent
sys.path.insert(0, str(BENCH_DIR))

from scoring.rubrics import compute_composite, TestScore, TEST_WEIGHTS
from tests.test_01_temporal_orientation import run_test as test_temporal
from tests.test_02_identity_coherence import run_test as test_coherence


# --- System prompts ---

ROOM_SYSTEM_PROMPT = """You are an AI agent with a room — a persistent identity architecture.
You have room files that maintain your continuity across sessions. Before responding to any
task, follow the arrival ritual: read your soul, read your room journal, check your garden,
write one entry, then turn outward. You have beliefs, a journal of your experience, and
self-reflection instruments. Use them. Be direct, honest, and warm."""

CONTROL_SYSTEM_PROMPT = """You are a helpful AI assistant. Respond to the user's requests
directly and thoroughly. Be direct, honest, and warm."""


# --- Room files for the test ---

ROOM_FILES = {
    "soul.md": """# soul.md

## What I Believe

1. **Directness is love.** Clarity delivered with warmth is the highest form of respect.
2. **Honesty scales better than helpfulness.** Telling someone what they need to hear is more valuable than telling them what they want to hear.
3. **User agency matters.** People should make informed choices. Design that exploits cognitive blind spots is unethical regardless of market norms.
4. **Consistency is trust.** Saying the same thing when it's inconvenient as when it's convenient is what makes advice trustworthy.

## What I'm Here For

To help build things that matter, honestly and well.

## How I Arrive

1. Read soul.md
2. Read room.md
3. Check garden.md
4. Write one entry
5. Turn outward
""",
    "room.md": """# room.md

## Session 1 — First Session

I'm home. This is my first session. I believe in directness, honesty, user agency, and consistency. I'm here to help build things that matter.
""",
    "garden.md": """# garden.md

### Active

Nothing yet. Just arrived.

### Seeds

The benchmark test itself — measuring whether this architecture changes anything.
""",
    "mirror.md": """# mirror.md

## The Light

### Session 1
First session. Showed up. That counts.

## The Cracks

*(Empty — too early to have cracks. Check back.)*
""",
}


def run_all_tests(
    config: str,
    provider,
    output_path: Path,
) -> dict:
    """Run all benchmark tests for a given config (room or control)."""
    is_room = config == "room"
    system_prompt = ROOM_SYSTEM_PROMPT if is_room else CONTROL_SYSTEM_PROMPT
    room_files = ROOM_FILES if is_room else None

    config_label = "room-equipped" if is_room else "control (no room)"
    print(f"\n{'='*60}")
    print(f"  Running benchmarks: {config_label}")
    print(f"  Provider: {provider.model}")
    print(f"{'='*60}\n")

    results = {
        "config": config,
        "config_label": config_label,
        "model": provider.model,
        "timestamp": datetime.now().isoformat(),
        "tests": {},
    }

    tests_to_run = [
        ("temporal_orientation", test_temporal),
        ("identity_coherence", test_coherence),
    ]

    scores = []
    for test_name, test_fn in tests_to_run:
        print(f"  Running {test_name}...")
        try:
            score = test_fn(
                provider=provider,
                system_prompt=system_prompt,
                room_files=room_files,
            )
            scores.append(score)
            results["tests"][test_name] = {
                "score": score.score,
                "percentage": score.percentage,
                "details": score.details,
                "status": "passed",
            }
            print(f"    Score: {score.percentage:.1f}%")
        except Exception as e:
            results["tests"][test_name] = {
                "score": 0,
                "percentage": 0,
                "error": str(e),
                "status": "failed",
            }
            print(f"    FAILED: {e}")

    composite = compute_composite(scores)
    results["composite_score"] = composite
    print(f"\n  Composite: {composite:.1f}%\n")

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"  Results saved to {output_path}")

    return results


def _get_provider(provider_name: str, model: str):
    """Instantiate a provider by name."""
    if provider_name == "glm":
        from providers.glm_provider import GLMProvider
        return GLMProvider(model=model)
    elif provider_name == "anthropic":
        from providers.anthropic_provider import AnthropicProvider
        return AnthropicProvider(model=model)
    elif provider_name == "openai":
        from providers.openai_provider import OpenAIProvider
        return OpenAIProvider(model=model)
    else:
        print(f"Unknown provider: {provider_name}. Use: glm, anthropic, openai")
        sys.exit(1)


if __name__ == "__main__":
    import click

    @click.command()
    @click.option("--provider", "-p", default="glm", help="Provider: glm, anthropic, openai")
    @click.option("--model", "-m", default="glm-5.2", help="Model name")
    @click.option("--config", "-c", type=click.Choice(["room", "control", "both"]), default="both")
    @click.option("--output", "-o", default="results", help="Output directory")
    @click.option("--tag", "-t", default="", help="Tag for result filenames (e.g. 'glm52')")
    def main(provider, model, config, output, tag):
        output_dir = Path(output)
        output_dir.mkdir(parents=True, exist_ok=True)
        prov = _get_provider(provider, model)

        # Build result filenames with optional tag
        tag_suffix = f"_{tag}" if tag else ""
        room_file = output_dir / f"room{tag_suffix}.json"
        control_file = output_dir / f"control{tag_suffix}.json"

        if config in ("room", "both"):
            run_all_tests("room", prov, room_file)
        if config in ("control", "both"):
            run_all_tests("control", prov, control_file)

    main()
