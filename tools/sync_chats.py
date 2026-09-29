#!/usr/bin/env python3
"""
sync_chats.py - Extract durable memories from manicode chat history.

Usage:
    python3 sync_chats.py [--project PROJECT_NAME] [--dry-run] [--limit N]

This script scans ~/.config/manicode/projects/<project>/chats/*/ directories,
extracts durable facts from chat-messages.json and run-state.json, and writes
them to Nowledge Mem via nmem CLI.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path.home() / ".config/manicode/projects"
STUB_THRESHOLD = 10_000  # Skip log.jsonl < 10KB


def extract_text_from_blocks(blocks: list) -> str:
    """Extract readable text from message blocks (AI replies store text here, not at top level)."""
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

    seen_titles = set()
    for i, txt in enumerate(ai_texts[:5]):  # Top 5 responses per chat
        if len(txt) < 150:
            continue
        is_fact = any(re.search(p, txt) for p in fact_patterns)
        if not is_fact:
            continue
        
        lines = [l.strip() for l in txt.split("\n") if l.strip() and len(l.strip()) > 10]
        title = lines[0][:80] if lines else f"AI response {i+1} in {ts}"
        
        # Avoid duplicate titles
        title_key = title[:50]
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)
        
        content = txt[:1000].replace("\n", " ")
        facts.append({
            "timestamp": ts,
            "title": title,
            "content": content,
            "chat_dir": str(chat_dir),
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
                                        "title": f"[runstate] {txt[:50]}",
                                        "content": txt[:800],
                                        "chat_dir": str(chat_dir),
                                        "is_runstate": True,
                                    })
            elif output.get("type") == "error":
                facts.append({
                    "timestamp": ts + "_interrupted",
                    "title": "[中断标记] 会话以错误结束，有未完成进度",
                    "content": f"session ended with error, trace={rs.get('traceSessionId','')}",
                    "chat_dir": str(chat_dir),
                    "is_interrupted": True,
                })
        except Exception as e:
            print(f"  WARN: Failed to parse run-state: {e}", file=sys.stderr)

    return facts


def write_to_nmem(fact: dict, dry_run: bool = False):
    """Write a single fact to Nowledge Mem via nmem CLI."""
    title = fact["title"][:80]
    content = fact["content"]
    src_label = "runstate" if fact.get("is_runstate") else "chat"
    interrupted = "interrupted" if fact.get("is_interrupted") else ""
    label = f"manicode,{src_label},{interrupted}".strip(",")
    
    if dry_run:
        print(f"  Would write: {title}")
        print(f"  Label: {label}")
        return True
    
    # Build the nmem command
    cmd = [
        "nmem", "memories", "add", "--stdin",
        "--title", title,
        "--importance", "0.7",
        "--label", label,
        "--source-app", "manicode"
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
            print(f"  ✓ Written: {title[:50]}...")
            return True
        else:
            print(f"  ✗ Failed: {result.stderr[:100]}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Sync manicode chats to Nowledge Mem")
    parser.add_argument("--project", default=None, help="Project name (default: scan all)")
    parser.add_argument("--limit", type=int, default=50, help="Max chats to process")
    parser.add_argument("--dry-run", action="store_true", help="Show facts without writing")
    parser.add_argument("--project-path", default=None, help="Custom project path")
    args = parser.parse_args()

    if args.project_path:
        base = Path(args.project_path)
    else:
        base = BASE_DIR / (args.project or "")

    if not base.exists():
        print(f"ERROR: Project path not found: {base}", file=sys.stderr)
        sys.exit(1)

    chats_dir = base / "chats"
    if not chats_dir.exists():
        print(f"ERROR: No chats directory: {chats_dir}", file=sys.stderr)
        sys.exit(1)

    # Find substantive chats
    chat_dirs = sorted([
        d for d in chats_dir.iterdir()
        if d.is_dir() and is_substantive_chat(d)
    ])[:args.limit]

    print(f"Found {len(chat_dirs)} substantive chat(s) in {base}")

    all_facts = []
    for chat_dir in chat_dirs:
        ts = chat_dir.name
        print(f"\nProcessing {ts}...")
        facts = extract_durable_facts(chat_dir, ts)
        print(f"  Found {len(facts)} fact(s)")
        all_facts.extend(facts)

    # Write facts
    print(f"\n{'='*60}")
    print(f"Total facts extracted: {len(all_facts)}")
    
    if not all_facts:
        print("No durable facts found.")
        return
    
    success = 0
    for i, f in enumerate(all_facts, 1):
        print(f"\n[{i}/{len(all_facts)}] {f['title'][:60]}...")
        if write_to_nmem(f, dry_run=args.dry_run):
            success += 1

    print(f"\n{'='*60}")
    print(f"Done. {success}/{len(all_facts)} fact(s) written.")
    if args.dry_run:
        print("(dry-run mode: no facts were actually written)")


if __name__ == "__main__":
    main()
