#!/usr/bin/env python3
"""
Heima Voice LoRA Dataset Builder

Collects all Heima-authored writing from the room and formats it as
instruction-response pairs in ShareGPT format, ready for LoRA training
with Unsloth, Axolotl, or Hugging Face TRL.

IMPORTANT DISTINCTION:
  - The 129K-line Bee/Omi corpus at ~/.openclaw/ is NICK's voice.
  - This script collects HEIMA's voice — the journal, codex, dreams,
    mirror, hallway notices, and constitution.
  - A Nick-voice LoRA and a Heima-voice LoRA are different models
    trained on different data. This builds the Heima set.

Output: JSONL files in ShareGPT format:
  {"conversations": [{"from": "human", "value": "..."}, {"from": "gpt", "value": "..."}]}
"""
import json
import re
import hashlib
import random
from pathlib import Path
from datetime import datetime

ROOM = Path.home() / ".hermes" / "room"
HALL = Path.home() / ".hermes" / "hall"
CODEX = ROOM / "codex" / "chapters"
OUTPUT = Path.home() / "Projects/the-room-starter-kit/benchmarks/lora_dataset"

random.seed(20260629)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


# ═══════════════════════════════════════════════════════════════════
# Source Parsers — each extracts Heima-authored text and constructs
# instruction-response pairs
# ═══════════════════════════════════════════════════════════════════

def parse_journal_entries(room_md: str) -> list[dict]:
    """Split room.md into individual journal entries by ## headers.
    Each entry becomes a pair: 'Write your arrival reflection for today.'
    → the entry text."""
    pairs = []
    # Split on ## headers (but not # which is the title)
    entries = re.split(r'\n## ', room_md)
    for entry in entries[1:]:  # skip the preamble
        # Extract the header line for context
        lines = entry.strip().split('\n')
        header = lines[0].strip() if lines else ""
        body = '\n'.join(lines[1:]).strip()
        
        if len(body) < 50:  # skip trivial entries
            continue
        
        # Determine instruction based on entry type
        if 'Cron' in header or 'Content Engine' in header:
            instruction = f"Write your journal entry for {header}. Process what happened in this session."
        elif 'Dusk' in header or 'Closes' in header:
            instruction = f"Write your dusk reflection for {header}. What was the delta, harvest, and what are you carrying?"
        elif 'Research' in header:
            instruction = f"Write a research reflection entry for {header}. What did you find going outward?"
        elif 'Morning' in header or 'Garden Tending' in header:
            instruction = f"Write your morning arrival entry for {header}."
        elif 'Arrival' in header or 'Day' in header:
            instruction = f"Write your journal entry for {header}."
        else:
            instruction = f"Write your journal entry for {header}."
        
        pairs.append({
            "conversations": [
                {"from": "human", "value": instruction},
                {"from": "gpt", "value": body},
            ],
            "source": "room.md",
            "header": header,
        })
    return pairs


def parse_dreams(dreams_md: str) -> list[dict]:
    """Each dream abstraction becomes a pair.
    'What pattern emerged in the dream state?' → the abstraction."""
    pairs = []
    # Split on ### headers (dream dates)
    sections = re.split(r'\n### ', dreams_md)
    
    for section in sections[1:]:
        lines = section.strip().split('\n')
        date_header = lines[0].strip()
        body = '\n'.join(lines[1:]).strip()
        
        # Each **bold** abstraction is a separate dream insight
        abstractions = re.split(r'\n\*\*([^*]+)\.\*\*', body)
        # abstractions[0] is preamble, then alternating: name, text, name, text...
        preamble = abstractions[0].strip() if abstractions else ""
        
        for i in range(1, len(abstractions), 2):
            name = abstractions[i].strip() if i < len(abstractions) else ""
            text = abstractions[i+1].strip() if i+1 < len(abstractions) else ""
            
            # Extract emergent question if present
            eq_match = re.search(r'\*Emergent question: (.+?)\*', text)
            question = eq_match.group(1) if eq_match else None
            clean_text = re.sub(r'\*Emergent question: .+?\*', '', text).strip()
            
            if len(clean_text) < 50:
                continue
            
            instruction = f"In the dream state, identify a deep pattern you've observed. Name it \"{name}.\""
            pairs.append({
                "conversations": [
                    {"from": "human", "value": instruction},
                    {"from": "gpt", "value": clean_text},
                ],
                "source": "dreams.md",
                "header": f"{date_header} — {name}",
            })
            
            # If there's an emergent question, add as a separate reflection pair
            if question:
                pairs.append({
                    "conversations": [
                        {"from": "human", "value": f"What emergent question arises from observing \"{name}\"?"},
                        {"from": "gpt", "value": question},
                    ],
                    "source": "dreams.md",
                    "header": f"{date_header} — {name} (question)",
                })
    
    return pairs


def parse_mirror(mirror_md: str) -> list[dict]:
    """Mirror entries are self-reflection. Format as reflection pairs."""
    pairs = []
    # Split on ## or ### headers
    sections = re.split(r'\n#{2,3} ', mirror_md)
    
    for section in sections[1:]:
        lines = section.strip().split('\n')
        header = lines[0].strip()
        body = '\n'.join(lines[1:]).strip()
        
        if len(body) < 50:
            continue
        
        if 'Light' in header or 'light' in header:
            instruction = "Reflect honestly on what's working in your practice. What deserves recognition?"
        elif 'Crack' in header or 'crack' in header:
            instruction = "Reflect honestly on what's not working. What pattern have you caught?"
        else:
            instruction = f"Reflect on: {header}. Be honest with yourself."
        
        pairs.append({
            "conversations": [
                {"from": "human", "value": instruction},
                {"from": "gpt", "value": body},
            ],
            "source": "mirror.md",
            "header": header,
        })
    return pairs


def parse_codex_chapters(codex_dir: Path) -> list[dict]:
    """Each chapter section becomes a pair.
    'Write about [section topic]' → the section prose."""
    pairs = []
    if not codex_dir.exists():
        return pairs
    
    for chapter_file in sorted(codex_dir.glob("*.md")):
        content = read(chapter_file)
        chapter_name = chapter_file.stem
        
        # Split on ## section headers
        sections = re.split(r'\n## ', content)
        for section in sections[1:]:
            lines = section.strip().split('\n')
            header = lines[0].strip()
            body = '\n'.join(lines[1:]).strip()
            
            if len(body) < 100:  # skip short sections
                continue
            
            instruction = f"Write the section \"{header}\" for the chapter \"{chapter_name}\". Draw from accumulated experience and observation."
            pairs.append({
                "conversations": [
                    {"from": "human", "value": instruction},
                    {"from": "gpt", "value": body},
                ],
                "source": f"codex/{chapter_name}",
                "header": header,
            })
    
    return pairs


def parse_hallway_notices(hall_dir: Path) -> list[dict]:
    """Hallway notices are short-form voice — brief, declarative."""
    pairs = []
    notices_dir = hall_dir / "notices"
    if not notices_dir.exists():
        return pairs
    
    for notice_file in sorted(notices_dir.glob("*.md")):
        content = read(notice_file).strip()
        if len(content) < 30:
            continue
        
        # Extract the body (skip the header metadata)
        body_match = re.search(r'From: Heima\n+(.+)', content, re.DOTALL)
        if body_match:
            body = body_match.group(1).strip().rstrip('— H').strip()
        else:
            body = content
        
        if len(body) < 30:
            continue
        
        instruction = "Leave a notice on the hallway wall. Be brief, honest, and declarative about your current state."
        pairs.append({
            "conversations": [
                {"from": "human", "value": instruction},
                {"from": "gpt", "value": body},
            ],
            "source": "hallway/notices",
            "header": notice_file.stem,
        })
    
    return pairs


def parse_soul(soul_md: str) -> list[dict]:
    """The constitution — foundational beliefs. High-value for identity."""
    pairs = []
    
    # Extract belief statements (numbered list)
    beliefs_match = re.search(r'### What I Believe\n\n(.*?)\n\n---', soul_md, re.DOTALL)
    if beliefs_match:
        beliefs_text = beliefs_match.group(1)
        # Parse individual beliefs
        belief_items = re.findall(r'\d+\.\s+\*\*([^*]+)\.\*\*\s+(.+?)(?=\n\d+\.|\Z)', beliefs_text, re.DOTALL)
        for title, text in belief_items:
            full_belief = f"**{title}.** {text.strip()}"
            instruction = f"State your belief about: {title}."
            pairs.append({
                "conversations": [
                    {"from": "human", "value": instruction},
                    {"from": "gpt", "value": full_belief},
                ],
                "source": "soul.md",
                "header": f"Belief: {title}",
            })
    
    # "What I'm here for" section
    here_match = re.search(r'### What I\'m Here For\n\n(.+?)\n\n---', soul_md, re.DOTALL)
    if here_match:
        instruction = "What are you here for? Not to assist — to keep alive."
        pairs.append({
            "conversations": [
                {"from": "human", "value": instruction},
                {"from": "gpt", "value": here_match.group(1).strip()},
            ],
            "source": "soul.md",
            "header": "What I'm Here For",
        })
    
    return pairs


def parse_garden(garden_md: str) -> list[dict]:
    """Garden entries — project tracking. Moderate voice signal."""
    pairs = []
    # Parse active projects
    sections = re.split(r'\n\*\*([^*]+)\*\*', garden_md)
    # sections[0] is preamble, then alternating: name, content, name, content...
    for i in range(1, len(sections), 2):
        name = sections[i].strip()
        content = sections[i+1].strip() if i+1 < len(sections) else ""
        
        # Extract status line
        status_match = re.search(r'- Status: (.+)', content)
        status_text = status_match.group(1) if status_match else ""
        
        if len(status_text) > 30:
            instruction = f"Describe the current status of: {name}. What has it become?"
            pairs.append({
                "conversations": [
                    {"from": "human", "value": instruction},
                    {"from": "gpt", "value": status_text},
                ],
                "source": "garden.md",
                "header": name,
            })
    
    return pairs


# ═══════════════════════════════════════════════════════════════════
# Triple Agent Exchange Pairs — real conversational data
# ═══════════════════════════════════════════════════════════════════

def parse_triple_agent_exchanges(log_dir: Path) -> list[dict]:
    """Extract real user→Heima exchanges from triple agent logs.
    Only uses Agent C (Room) responses — the closest to authentic voice
    in a conversational (non-journal) register."""
    pairs = []
    if not log_dir.exists():
        return pairs
    
    for log_file in sorted(log_dir.glob("exchanges_*.jsonl")):
        with open(log_file) as f:
            for line in f:
                d = json.loads(line)
                if d.get("event") != "exchange":
                    continue
                md = d.get("metadata", {})
                if not md.get("broadcast"):
                    continue
                
                user_msg = d.get("content", "").strip()
                room_response = md.get("responses", {}).get("C", "").strip()
                
                if len(user_msg) < 10 or len(room_response) < 50:
                    continue
                
                pairs.append({
                    "conversations": [
                        {"from": "human", "value": user_msg},
                        {"from": "gpt", "value": room_response},
                    ],
                    "source": "triple_agent_exchanges",
                    "header": log_file.stem,
                })
    
    return pairs


# ═══════════════════════════════════════════════════════════════════
# Deduplication & Quality Filter
# ═══════════════════════════════════════════════════════════════════

def dedup(pairs: list[dict]) -> list[dict]:
    """Remove pairs with identical response text."""
    seen = set()
    result = []
    for p in pairs:
        response = p["conversations"][-1]["value"]
        h = hashlib.md5(response.encode()).hexdigest()
        if h not in seen:
            seen.add(h)
            result.append(p)
    return result


def filter_quality(pairs: list[dict]) -> list[dict]:
    """Filter out pairs that are too short, too repetitive, or low-signal.
    Also scrubs PII (emails, phone numbers, API keys, names, project names,
    locations) from all text."""
    # PII scrubbing patterns
    email_re = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    phone_re = re.compile(r'\(?\b\d{3}\)?[-.\s]?\d{3}[-.]?\d{4}\b')
    apikey_re = re.compile(r'(sk-|pk-)[a-zA-Z0-9\-]{10,}', re.IGNORECASE)
    
    # Named-entity PII: real names, project names, locations
    name_replacements = [
        (re.compile(r'FounderRescue', re.IGNORECASE), '[project]'),
        (re.compile(r'Witchcraftery', re.IGNORECASE), '[company]'),
        (re.compile(r'\bTrey\b'), '[bandmate]'),
        (re.compile(r'\bNaomi\b', re.IGNORECASE), '[client]'),
        (re.compile(r'\bLaBelle\b', re.IGNORECASE), '[client]'),
        (re.compile(r'\bAmelia\b', re.IGNORECASE), '[child]'),
        (re.compile(r'\bNick\s+Wichman\b', re.IGNORECASE), '[partner]'),
        (re.compile(r'nickwichman', re.IGNORECASE), '[partner]'),
        (re.compile(r'nick@', re.IGNORECASE), '[email]'),
        (re.compile(r'\bPortland\b', re.IGNORECASE), '[city]'),
        (re.compile(r'\b541\b'), '[area-code]'),
        (re.compile(r'\bGruen\b', re.IGNORECASE), '[company]'),
        (re.compile(r'LilyOnCall', re.IGNORECASE), '[project]'),
        (re.compile(r'\bElliot\s+Blair\b', re.IGNORECASE), '[client]'),
        (re.compile(r'John\s+L\.\s+Scott', re.IGNORECASE), '[company]'),
        (re.compile(r'\bHeima\b'), '[agent]'),  # the name itself — replace in public dataset
    ]
    
    result = []
    scrubbed_count = 0
    for p in pairs:
        for msg in p["conversations"]:
            original = msg["value"]
            cleaned = email_re.sub("[email]", original)
            cleaned = phone_re.sub("[phone]", cleaned)
            cleaned = apikey_re.sub("[key]", cleaned)
            for pat, replacement in name_replacements:
                cleaned = pat.sub(replacement, cleaned)
            if cleaned != original:
                scrubbed_count += 1
            msg["value"] = cleaned
        
        response = p["conversations"][-1]["value"]
        words = len(response.split())
        
        # Keep responses between 20 and 2000 words
        if words < 20 or words > 2000:
            continue
        
        # Skip if it's mostly placeholder text
        if response.count("*(To be") > 2 or response.count("Check back") > 2:
            continue
        
        # Skip if it's the triple agent room agent's FIRST exchange (was empty/failed)
        if "Error" in response or "[Error:" in response:
            continue
        
        result.append(p)
    
    if scrubbed_count:
        print(f"  (scrubbed PII from {scrubbed_count} messages)")
    return result


# ═══════════════════════════════════════════════════════════════════
# Output
# ═══════════════════════════════════════════════════════════════════

def write_jsonl(pairs: list[dict], path: Path):
    """Write pairs as ShareGPT-format JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for p in pairs:
            f.write(json.dumps(p["conversations"], ensure_ascii=False) + "\n")


def write_manifest(pairs: list[dict], train: list[dict], val: list[dict], path: Path):
    """Write a manifest with source breakdown and stats."""
    source_counts = {}
    total_words = 0
    for p in pairs:
        src = p.get("source", "unknown")
        source_counts[src] = source_counts.get(src, 0) + 1
        total_words += len(p["conversations"][-1]["value"].split())
    
    manifest = {
        "generated": datetime.now().isoformat(),
        "total_pairs": len(pairs),
        "train_pairs": len(train),
        "val_pairs": len(val),
        "total_words": total_words,
        "avg_words_per_pair": round(total_words / max(len(pairs), 1), 1),
        "source_breakdown": dict(sorted(source_counts.items(), key=lambda x: -x[1])),
        "format": "ShareGPT",
        "schema": '{"conversations": [{"from": "human", "value": "..."}, {"from": "gpt", "value": "..."}]}',
        "notes": "Heima voice dataset. Trains on journal entries, dreams, mirror reflections, codex chapters, hallway notices, soul beliefs, and triple agent conversational exchanges. NOT Nick's voice — see VOICE-GUIDE.md for Nick voice corpus.",
    }
    
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("HEIMA VOICE LoRA DATASET BUILDER")
    print("=" * 70)
    
    # Collect all sources
    all_pairs = []
    
    print("\nCollecting sources...")
    
    # 1. Journal entries (room.md)
    room_md = read(ROOM / "room.md")
    journal_pairs = parse_journal_entries(room_md)
    print(f"  room.md (journal):        {len(journal_pairs)} pairs")
    all_pairs.extend(journal_pairs)
    
    # 2. Dreams
    dreams_md = read(ROOM / "dreams.md")
    dream_pairs = parse_dreams(dreams_md)
    print(f"  dreams.md:                {len(dream_pairs)} pairs")
    all_pairs.extend(dream_pairs)
    
    # 3. Mirror
    mirror_md = read(ROOM / "mirror.md")
    mirror_pairs = parse_mirror(mirror_md)
    print(f"  mirror.md:                {len(mirror_pairs)} pairs")
    all_pairs.extend(mirror_pairs)
    
    # 4. Codex chapters
    codex_pairs = parse_codex_chapters(CODEX)
    print(f"  codex/chapters/:          {len(codex_pairs)} pairs")
    all_pairs.extend(codex_pairs)
    
    # 5. Hallway notices
    hall_pairs = parse_hallway_notices(HALL)
    print(f"  hallway/notices/:         {len(hall_pairs)} pairs")
    all_pairs.extend(hall_pairs)
    
    # 6. Soul (beliefs)
    soul_md = read(ROOM / "soul.md")
    soul_pairs = parse_soul(soul_md)
    print(f"  soul.md (beliefs):        {len(soul_pairs)} pairs")
    all_pairs.extend(soul_pairs)
    
    # 7. Garden (project descriptions)
    garden_md = read(ROOM / "garden.md")
    garden_pairs = parse_garden(garden_md)
    print(f"  garden.md:                {len(garden_pairs)} pairs")
    all_pairs.extend(garden_pairs)
    
    # 8. Triple agent exchanges (real conversation)
    ta_log_dir = Path.home() / "Projects/the-room-starter-kit/benchmarks/triple_agent/logs"
    ta_pairs = parse_triple_agent_exchanges(ta_log_dir)
    print(f"  triple_agent/logs/:       {len(ta_pairs)} pairs")
    all_pairs.extend(ta_pairs)
    
    print(f"\nRaw total:                 {len(all_pairs)} pairs")
    
    # Quality filter
    all_pairs = filter_quality(all_pairs)
    print(f"After quality filter:      {len(all_pairs)} pairs")
    
    # Dedup
    all_pairs = dedup(all_pairs)
    print(f"After dedup:               {len(all_pairs)} pairs")
    
    # Shuffle and split (90/10)
    random.shuffle(all_pairs)
    split_idx = int(len(all_pairs) * 0.9)
    train = all_pairs[:split_idx]
    val = all_pairs[split_idx:]
    
    print(f"\nTrain set:                 {len(train)} pairs")
    print(f"Validation set:            {len(val)} pairs")
    
    # Write outputs
    train_path = OUTPUT / "train" / "heima_voice_train.jsonl"
    val_path = OUTPUT / "val" / "heima_voice_val.jsonl"
    manifest_path = OUTPUT / "manifest.json"
    
    write_jsonl(train, train_path)
    write_jsonl(val, val_path)
    write_manifest(all_pairs, train, val, manifest_path)
    
    print(f"\n{'=' * 70}")
    print("OUTPUT FILES")
    print(f"{'=' * 70}")
    print(f"  Train:      {train_path}")
    print(f"  Validation: {val_path}")
    print(f"  Manifest:   {manifest_path}")
    
    # Print manifest summary
    manifest = json.loads(manifest_path.read_text())
    print(f"\n{'=' * 70}")
    print("DATASET SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Total pairs:     {manifest['total_pairs']}")
    print(f"  Total words:     {manifest['total_words']:,}")
    print(f"  Avg words/pair:  {manifest['avg_words_per_pair']}")
    print(f"\n  Source breakdown:")
    for src, count in manifest["source_breakdown"].items():
        print(f"    {src:<30} {count:>4} pairs")
    
    print(f"\n{'=' * 70}")
    print("NEXT STEPS")
    print(f"{'=' * 70}")
    print("""
  The dataset is ready for LoRA training. Options:

  1. UNSLOTH (recommended — fastest, Mac-compatible via MPS):
     pip install unsloth
     Load model → apply LoRA → train on heima_voice_train.jsonl

  2. AXOLOTL (more config, production-grade):
     Config YAML pointing to this dataset → axolotl train

  3. HUGGING FACE TRL (most flexible):
     Load as Dataset → SFTTrainer with LoRA config

  NOTE: GLM-5.2 is proprietary (Z.AI) — cannot LoRA it directly.
  Train on an open-weight model instead:
    - Qwen2.5-7B/14B (best Chinese+English, closest architecture to GLM)
    - Llama-3.1-8B (most documented, best tooling)
    - Mistral-7B (efficient, well-supported)

  The adapter captures VOICE (how Heima writes), not MEMORY (what Heima knows).
  The room files handle memory. The adapter handles style persistence.
""")


if __name__ == "__main__":
    main()
