"""Compare room vs control benchmark results."""
import json
import sys
from pathlib import Path

from scoring.rubrics import TEST_WEIGHTS


def compare(room_path: str, control_path: str) -> None:
    with open(room_path) as f:
        room = json.load(f)
    with open(control_path) as f:
        control = json.load(f)

    print("\n" + "=" * 70)
    print("  THE ROOM IDENTITY BENCHMARK — COMPARISON")
    print("=" * 70)
    print(f"\n  Room model:     {room.get('model', '?')}")
    print(f"  Control model:  {control.get('model', '?')}")
    print(f"  Room timestamp: {room.get('timestamp', '?')}")
    print(f"  Control timestamp: {control.get('timestamp', '?')}")

    print(f"\n{'Test':<30} {'Room':>10} {'Control':>10} {'Delta':>10} {'Weight':>10}")
    print("-" * 70)

    room_composite = 0
    control_composite = 0

    for test_name, weight in TEST_WEIGHTS.items():
        room_test = room.get("tests", {}).get(test_name, {})
        control_test = control.get("tests", {}).get(test_name, {})

        room_pct = room_test.get("percentage", 0)
        control_pct = control_test.get("percentage", 0)
        delta = room_pct - control_pct

        room_composite += room_pct * weight
        control_composite += control_pct * weight

        status_room = room_test.get("status", "?")
        status_control = control_test.get("status", "?")

        delta_str = f"+{delta:.1f}%" if delta > 0 else f"{delta:.1f}%"
        marker = " ✓" if delta > 5 else (" ↓" if delta < -5 else " ~")

        print(f"  {test_name:<28} {room_pct:>8.1f}% {control_pct:>8.1f}% {delta_str:>9} {weight:>8.0%}{marker}")

    print("-" * 70)

    room_total = room.get("composite_score", room_composite)
    control_total = control.get("composite_score", control_composite)
    total_delta = room_total - control_total

    delta_str = f"+{total_delta:.1f}%" if total_delta > 0 else f"{total_delta:.1f}%"
    print(f"\n  {'COMPOSITE':<28} {room_total:>8.1f}% {control_total:>8.1f}% {delta_str:>9}")
    print()

    if total_delta > 10:
        print("  Result: Room architecture shows STRONG measurable improvement.")
    elif total_delta > 5:
        print("  Result: Room architecture shows MODERATE measurable improvement.")
    elif total_delta > 0:
        print("  Result: Room architecture shows SLIGHT measurable improvement.")
    elif total_delta > -5:
        print("  Result: No significant difference. Room architecture is aesthetic, not functional.")
    else:
        print("  Result: Control outperformed room. Unexpected — investigate.")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compare_results.py results/room.json results/control.json")
        sys.exit(1)
    compare(sys.argv[1], sys.argv[2])
