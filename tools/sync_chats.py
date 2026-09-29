#!/usr/bin/env python3
"""
sync_chats.py - Extract durable memories from manicode chat history.

Usage:
    # Incremental sync (default) - only process new/updated chats
    python3 sync_chats.py --project PROJECT_NAME
    
    # Full re-sync - process all chats
    python3 sync_chats.py --project PROJECT_NAME --full
    
    # Dry run - show what would be synced
    python3 sync_chats.py --project PROJECT_NAME --dry-run

State file: ~/.config/manicode/projects/<project>/.sync-state.json
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path.home() / ".config/manicode/projects"
STUB_THRESHOLD = 10_000  # Skip log.jsonl < 10KB
SYNC_STATE_FILE = ".sync-state.json"


def get_chat_hash(chat_dir: Path) -> str:
    """Calculate hash of chat directory for change detection."""
    msgs_file = chat_dir / "chat-messages.json"
    if not msgs_file.exists():
        return None
    
    # Hash the file content
    with open(msgs_file, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def load_sync_state(project_path: Path) -> dict:
    """Load previous sync state."""
    state_file = project_path / SYNC_STATE_FILE
    if state_file.exists():
        try:
            with open(state_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"chats": {}, "last_sync": None}


def save_sync_state(project_path: Path, state: dict):
    """Save sync state."""
    state_file = project_path / SYNC_STATE_FILE
    state["last_sync"] = datetime.now().isoformat()
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def extract_text_from_blocks(blocks: list) -> str:
    """Extract readable text from message blocks."""
    parts = []
    for b in blocks:
        if b.get("type") == "text":
            c = b.get("content", "")
            if isinstance(c, str):
                parts.append(c)
            elif isinstance(c, list):
                for item in c:
                    if isinstance(item, dict) and item.get("type") == "text":
                        parts.append(item.get("text", ""))
    return "\n".join(parts).strip()


def is_substantive_chat(chat_dir: Path) -> bool:
    """Check if this chat directory has meaningful content."""
    msgs_file = chat_dir / "chat-messages.json"
    if not msgs_file.exists():
        return False
    size = msgs_file.stat().st_size
    return size > 400_000  # > 400KB = substantive conversation


def extract_durable_facts(chat_dir: Path, ts: str) -> list:
    """Extract durable facts from a chat directory."""
    facts = []
    msgs_file = chat_dir / "chat-messages.json"
    runstate_file = chat_dir / "run-state.json"

    if not msgs_file.exists():
        return facts

    try:
        with open(msgs_file, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"  WARN: Failed to parse {msgs_file}: {e}", file=sys.stderr)
        return facts

    # Extract AI responses from blocks
    ai_msgs = [m for m in data if m.get("variant") == "ai" and m.get("blocks")]
    ai_texts = [
        extract_text_from_blocks(m["blocks"])
        for m in ai_msgs
        if extract_text_from_blocks(m["blocks"])
    ]

    # Find concrete facts
    fact_patterns = [
        r"\d{6,}-signed\.bin", r"commit\s+[a-f0-9]{7,}", r"0x[0-9a-fA-F]{4,}",
        r"\.md\b", r"\.py\b", r"\.c\b", r"\.h\b", r"BUGS\.",
        r"已修复|已提交|已确认|根因|解决方案|约束|规范",
        r"slot.*size|partition.*offset|nvs.*offset",
    ]

    for i, txt in enumerate(ai_texts[:5]):
        if not any(re.search(p, txt) for p in fact_patterns):
            continue
        
        lines = [l.strip() for l in txt.split("\n") if l.strip() and len(l.strip()) > 10]
        title = lines[0][:80] if lines else f"Fact from {ts}"
        
        facts.append({
            "timestamp": ts,
            "title": title,
            "content": txt[:1000],
            "source": str(chat_dir),
        })

    # Extract run-state final status
    if runstate_file.exists():
        try:
            with open(runstate_file) as f:
                rs = json.load(f)
            output = rs.get("output", {})
            
            if output.get("type") == "lastMessage":
                for m in output.get("value", []):
                    if isinstance(m, dict):
                        for c in m.get("content", []):
                            if isinstance(c, dict) and c.get("type") == "text":
                                txt = c.get("text", "").strip()
                                if txt and len(txt) > 100:
                                    facts.append({
                                        "timestamp": ts + "_runstate",
                                        "title": f"[交付物] {txt[:50]}",
                                        "content": txt[:800],
                                        "source": str(chat_dir),
                                        "is_delivery": True,
                                    })
            elif output.get("type") == "error":
                facts.append({
                    "timestamp": ts + "_interrupted",
                    "title": "[中断标记] 会话以错误结束，有未完成进度",
                    "content": f"session ended with error, trace={rs.get('traceSessionId','')}",
                    "source": str(chat_dir),
                    "is_interrupted": True,
                })
        except Exception as e:
            print(f"  WARN: Failed to parse run-state: {e}", file=sys.stderr)

    return facts


def write_to_nmem(fact: dict, dry_run: bool = False) -> bool:
    """Write a single fact to Nowledge Mem via nmem CLI."""
    title = fact["title"][:80]
    content = fact["content"]
    is_interrupted = fact.get("is_interrupted", False)
    
    # Determine importance based on content type
    if is_interrupted:
        importance = 0.9  # High priority: incomplete work needs attention
    elif "bug" in title.lower() or "根因" in title:
        importance = 0.8
    else:
        importance = 0.7
    
    # Determine labels
    labels = ["manicode-sync"]
    if "meta-pass" in fact.get("source", ""):
        labels.append("meta-pass")
    elif "pass-radar" in fact.get("source", ""):
        labels.append("pass-radar")
    if is_interrupted:
        labels.append("incomplete")
    
    label_str = ",".join(labels)
    
    if dry_run:
        print(f"  Would write: {title}")
        return True
    
    # Build nmem command
    cmd = [
        "nmem", "memories", "add", "--stdin",
        "--title", title,
        "--importance", str(importance),
        "--label", label_str,
        "--source-app", "freebuff2nmem"
    ]
    
    try:
        result = subprocess.run(
            cmd,
            input=content,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return True
        else:
            print(f"  ERROR: {result.stderr[:100]}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Sync manicode chats to Nowledge Mem")
    parser.add_argument("--project", default=None, help="Project name (default: scan all)")
    parser.add_argument("--project-path", default=None, help="Custom project path")
    parser.add_argument("--limit", type=int, default=50, help="Max chats to process")
    parser.add_argument("--full", action="store_true", help="Full re-sync (ignore state)")
    parser.add_argument("--dry-run", action="store_true", help="Show facts without writing")
    args = parser.parse_args()

    # Determine base path
    if args.project_path:
        base = Path(args.project_path)
    elif args.project:
        base = BASE_DIR / args.project
    else:
        # Scan all projects
        base = BASE_DIR
    
    if not base.exists():
        print(f"ERROR: Path not found: {base}", file=sys.stderr)
        sys.exit(1)

    chats_dir = base / "chats"
    if not chats_dir.exists():
        print(f"ERROR: No chats directory: {chats_dir}", file=sys.stderr)
        sys.exit(1)

    # Load sync state
    state = load_sync_state(base)
    synced_chats = state.get("chats", {})
    
    # Find all substantive chats
    all_chats = sorted([
        d for d in chats_dir.iterdir()
        if d.is_dir() and is_substantive_chat(d)
    ])[:args.limit]

    # Determine which chats to process
    if args.full:
        chats_to_process = all_chats
        print(f"Full sync: processing {len(chats_to_process)} chat(s)")
    else:
        # Incremental: only new or updated chats
        chats_to_process = []
        for chat_dir in all_chats:
            ts = chat_dir.name
            current_hash = get_chat_hash(chat_dir)
            last_hash = synced_chats.get(ts, {}).get("hash")
            
            if current_hash != last_hash:
                chats_to_process.append(chat_dir)
        
        print(f"Incremental sync: {len(chats_to_process)} new/updated chat(s) found")
        if not chats_to_process and synced_chats:
            print(f"Last sync: {state.get('last_sync', 'unknown')}")
            print("All chats are up to date.")
            return

    # Process chats
    all_facts = []
    updated_states = {}
    
    for chat_dir in chats_to_process:
        ts = chat_dir.name
        print(f"\nProcessing {ts}...")
        
        # Update hash
        current_hash = get_chat_hash(chat_dir)
        updated_states[ts] = {"hash": current_hash, "timestamp": datetime.now().isoformat()}
        
        # Extract facts
        facts = extract_durable_facts(chat_dir, ts)
        print(f"  Found {len(facts)} fact(s)")
        all_facts.extend(facts)

    # Write facts
    if not all_facts:
        print("\nNo new durable facts found.")
        return
    
    print(f"\n{'='*60}")
    print(f"Total facts to process: {len(all_facts)}")
    
    success = 0
    for i, f in enumerate(all_facts, 1):
        print(f"\n[{i}/{len(all_facts)}] {f['title'][:60]}...")
        if write_to_nmem(f, dry_run=args.dry_run):
            success += 1

    # Save sync state
    if not args.dry_run:
        state["chats"] = {**synced_chats, **updated_states}
        save_sync_state(base, state)
        print(f"\nSync state saved to {(base / SYNC_STATE_FILE).resolve()}")

    print(f"\n{'='*60}")
    print(f"Done. {success}/{len(all_facts)} fact(s) written.")
    if args.dry_run:
        print("(dry-run mode: no facts were actually written)")
    else:
        print(f"Next sync will only process new/updated chats.")


if __name__ == "__main__":
    main()
