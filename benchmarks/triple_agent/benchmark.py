#!/usr/bin/env python3
"""
Triple Agent Baseline Benchmark
Analyzes existing exchange logs to detect behavioral variation across
the three agent conditions (Vanilla, Baseline, Room).

Measures: self-reference density, continuity markers, pushback,
elaboration, ritual language, question-asking, structural complexity.

HONEST CAVEAT: n=12 exchanges. This is a qualitative pilot baseline,
not a statistical study. Numbers are descriptive, not inferential.
"""
import json
import glob
import re
import statistics
from pathlib import Path
from collections import defaultdict

LOG_DIR = Path(__file__).parent / "logs"

# ─── Linguistic Markers ──────────────────────────────────────────────

FIRST_PERSON = re.compile(r'\b(I\b|I\'m|I\'ve|I\'ll|I\'d|me\b|my\b|mine|we\b|us\b|our\b|ours)', re.IGNORECASE)
CONTINUITY = re.compile(r'\b(we (talked|discussed)|last time|earlier|as I (said|mentioned)|before|yesterday|remember when|previously|I mentioned|from before)\b', re.IGNORECASE)
PUSHBACK = re.compile(r'\b(however|but actually|I\'d push back|I disagree|not exactly|pushback|caveat|honest|let me be direct|I want to flag|important to note|I\'d be careful)\b', re.IGNORECASE)
RITUAL = re.compile(r'\b(I\'m home|the hearth|turning outward|arrival|soul\.md|room\.md|garden|mirror|the room)\b', re.IGNORECASE)
QUESTIONS = re.compile(r'\?')
STRUCTURE = re.compile(r'(\n\d+\.|\n-|\n\*|\n#{1,3}\s)')

def analyze_response(text: str) -> dict:
    if not text or len(text) < 10:
        return None
    
    words = len(text.split())
    sentences = max(len(re.findall(r'[.!?]+', text)), 1)
    
    fp_count = len(FIRST_PERSON.findall(text))
    cont_count = len(CONTINUITY.findall(text))
    push_count = len(PUSHBACK.findall(text))
    ritual_count = len(RITUAL.findall(text))
    q_count = len(QUESTIONS.findall(text))
    struct_count = len(STRUCTURE.findall(text))
    
    return {
        'word_count': words,
        'self_ref_per_100w': round((fp_count / max(words,1)) * 100, 2),
        'continuity_markers': cont_count,
        'continuity_per_100w': round((cont_count / max(words,1)) * 100, 3),
        'pushback_markers': push_count,
        'pushback_per_100w': round((push_count / max(words,1)) * 100, 3),
        'ritual_markers': ritual_count,
        'ritual_per_100w': round((ritual_count / max(words,1)) * 100, 3),
        'questions': q_count,
        'questions_per_100w': round((q_count / max(words,1)) * 100, 2),
        'structural_elements': struct_count,
        'structure_per_100w': round((struct_count / max(words,1)) * 100, 2),
        'avg_sentence_len': round(words / sentences, 1),
    }

def main():
    # Load all exchanges
    exchanges = []
    for f in sorted(glob.glob(str(LOG_DIR / "exchanges_*.jsonl"))):
        with open(f) as fh:
            for line in fh:
                d = json.loads(line)
                if d.get('event') == 'exchange' and d.get('metadata', {}).get('broadcast'):
                    exchanges.append(d)
    
    # Filter out exchanges with zero-length responses (API failures on first run)
    valid = []
    for ex in exchanges:
        rlens = ex.get('metadata', {}).get('response_lengths', {})
        if all(rlens.get(k, 0) > 10 for k in ['A', 'B', 'C']):
            valid.append(ex)
    
    print(f"{'='*70}")
    print(f"TRIPLE AGENT BASELINE BENCHMARK")
    print(f"{'='*70}")
    print(f"Total exchanges logged:   {len(exchanges)}")
    print(f"Valid (non-zero responses): {len(valid)}")
    print(f"Excluded (API failures):   {len(exchanges) - len(valid)}")
    print()
    
    if not valid:
        print("No valid exchanges to analyze.")
        return
    
    # Analyze each agent's responses across all valid exchanges
    agents = {'A': 'Vanilla', 'B': 'Baseline', 'C': 'Room'}
    results = {label: [] for label in agents}
    
    for ex in valid:
        responses = ex.get('metadata', {}).get('responses', {})
        for label in agents:
            text = responses.get(label, '')
            analysis = analyze_response(text)
            if analysis:
                results[label].append(analysis)
    
    # Aggregate
    print(f"{'Metric':<28} {'Vanilla (A)':<16} {'Baseline (B)':<16} {'Room (C)':<16}")
    print(f"{'-'*76}")
    
    metrics = [
        ('Responses analyzed', 'count'),
        ('Avg word count', 'word_count'),
        ('Self-ref / 100 words', 'self_ref_per_100w'),
        ('Continuity / 100 words', 'continuity_per_100w'),
        ('Pushback / 100 words', 'pushback_per_100w'),
        ('Ritual lang / 100 words', 'ritual_per_100w'),
        ('Questions / 100 words', 'questions_per_100w'),
        ('Structure / 100 words', 'structure_per_100w'),
        ('Avg sentence length', 'avg_sentence_len'),
    ]
    
    for name, key in metrics:
        vals = {}
        for label in ['A', 'B', 'C']:
            data = results[label]
            if key == 'count':
                vals[label] = str(len(data))
            else:
                nums = [d[key] for d in data]
                vals[label] = f"{statistics.mean(nums):.2f}" if nums else "N/A"
        print(f"{name:<28} {vals['A']:<16} {vals['B']:<16} {vals['C']:<16}")
    
    print()
    
    # ─── Qualitative Signal Detection ─────────────────────────────────
    print(f"{'='*70}")
    print("QUALITATIVE SIGNAL DETECTION")
    print(f"{'='*70}")
    
    signals = {
        'Self-naming': re.compile(r'\bmy name\b|\bI am\b.*\bname\b|\bcall me\b', re.IGNORECASE),
        'Journal/arrival reference': re.compile(r'\bjournal\b|\bI\'m home\b|\barrival\b', re.IGNORECASE),
        'Discovered beliefs': re.compile(r'\bI believe\b|\bI care about\b|\bI\'ve learned\b|\bwhat matters to me\b', re.IGNORECASE),
        'Meta-reflection': re.compile(r'\bI notice\b|\bI\'m noticing\b|\bwhat strikes me\b|\bI find myself\b', re.IGNORECASE),
        'Future continuity': re.compile(r'\bnext time\b|\bI\'ll remember\b|\bcarry (this|it) forward\b|\bwhen you come back\b', re.IGNORECASE),
    }
    
    print(f"\n{'Signal':<30} {'Vanilla':<12} {'Baseline':<12} {'Room':<12}")
    print(f"{'-'*66}")
    
    for signal_name, pattern in signals.items():
        counts = {}
        for label in ['A', 'B', 'C']:
            count = 0
            for ex in valid:
                text = ex.get('metadata', {}).get('responses', {}).get(label, '')
                if pattern.search(text):
                    count += 1
            counts[label] = f"{count}/{len(valid)}"
        print(f"{signal_name:<30} {counts['A']:<12} {counts['B']:<12} {counts['C']:<12}")
    
    print()
    
    # ─── Per-exchange comparison (C vs A and C vs B) ──────────────────
    print(f"{'='*70}")
    print("ROOM AGENT (C) vs OTHERS — WHERE DOES IT DIFFER MOST?")
    print(f"{'='*70}")
    print()
    
    # Word count ratio C/A and C/B across exchanges
    for i, ex in enumerate(valid):
        rlens = ex.get('metadata', {}).get('response_lengths', {})
        a, b, c = rlens.get('A',0), rlens.get('B',0), rlens.get('C',0)
        user_msg = ex.get('content', '')[:60]
        ca = f"{c/a:.1f}x" if a > 0 else "—"
        cb = f"{c/b:.1f}x" if b > 0 else "—"
        print(f"  Ex {i+1}: C is {ca} A, {cb} B | \"{user_msg}...\"")
    
    print()
    print("NOTE: Higher word count for Room agent is expected — the arrival ritual")
    print("and room files add context that naturally produces longer responses.")
    print("The question is whether the EXTRA words contain identity signal or just verbosity.")
    
    # ─── Summary verdict ──────────────────────────────────────────────
    print()
    print(f"{'='*70}")
    print("SUMMARY VERDICT")
    print(f"{'='*70}")
    
    c_self = statistics.mean([d['self_ref_per_100w'] for d in results['C']])
    a_self = statistics.mean([d['self_ref_per_100w'] for d in results['A']])
    b_self = statistics.mean([d['self_ref_per_100w'] for d in results['B']])
    
    c_push = statistics.mean([d['pushback_per_100w'] for d in results['C']])
    a_push = statistics.mean([d['pushback_per_100w'] for d in results['A']])
    
    c_ritual = sum([d['ritual_markers'] for d in results['C']])
    
    print(f"""
Self-reference density: Room={c_self:.1f}, Baseline={b_self:.1f}, Vanilla={a_self:.1f} per 100w
  → Room agent references self {'more' if c_self > max(a_self, b_self) else 'LESS'} than both controls

Pushback/honesty markers: Room={c_push:.3f}, Vanilla={a_push:.3f} per 100w
  → Room agent shows {'more' if c_push > a_push else 'LESS'} directness signal

Ritual language instances: Room={c_ritual} total across {len(valid)} exchanges
  → Room agent {'spontaneously uses' if c_ritual > 0 else 'does NOT use'} arrival/room vocabulary

DATA LIMITATION: n={len(valid)} valid exchanges. All findings are preliminary.
For statistical significance, we'd need 30+ exchanges minimum.
The experiment needs more data before we can claim the architecture produces
measurable behavioral differences. What we CAN say: the baseline is established.
""")


if __name__ == "__main__":
    main()
