"""Triple Agent Parallel Harness — Telegram Bot Interface.

A dedicated Telegram bot that fans out user messages to three agents
and returns three labeled responses. Supports reply-to for directed
follow-ups to a single agent.
"""
import json
import logging
import os
import re
import time
from pathlib import Path

import requests
from harness import TripleAgentHarness

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("triple-agent")

# ─── Telegram Bot Helpers ────────────────────────────────────────────

BOT_TOKEN = os.getenv("TRIPLE_AGENT_BOT_TOKEN", "")
API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"


def tg_send(chat_id: int, text: str, reply_to: int = None) -> dict:
    """Send a message via Telegram bot API. Returns the response (includes message_id)."""
    # Telegram message limit is 4096 chars
    if len(text) > 4000:
        text = text[:3990] + "\n\n[...truncated]"
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }
    if reply_to:
        payload["reply_to_message_id"] = reply_to
    
    resp = requests.post(f"{API_BASE}/sendMessage", json=payload, timeout=30)
    data = resp.json()
    if not data.get("ok"):
        log.error(f"Telegram send failed: {data}")
    return data


def tg_get_updates(offset: int = None, timeout: int = 30) -> list:
    """Long-poll for new updates."""
    params = {"timeout": timeout}
    if offset:
        params["offset"] = offset
    resp = requests.get(f"{API_BASE}/getUpdates", params=params, timeout=timeout + 10)
    data = resp.json()
    return data.get("result", [])


# ─── Agent Labels ───────────────────────────────────────────────────

AGENT_LABELS = {
    "A": "🅰️ Vanilla",
    "B": "🅱️ Baseline", 
    "C": "🏠 Room",
}


def format_response(label: str, agent_name: str, response: str) -> str:
    """Format an agent's response with a clear label prefix."""
    name = AGENT_LABELS.get(label, label)
    # Escape markdown special chars in the response body minimally
    return f"*{name}*\n\n{response}"


# ─── Main Bot Loop ──────────────────────────────────────────────────

def run_bot():
    """Run the triple-agent Telegram bot."""
    if not BOT_TOKEN:
        print("ERROR: TRIPLE_AGENT_BOT_TOKEN not set in environment.")
        print("Create a bot via @BotFather and add the token to ~/.hermes/.env")
        return
    
    # Initialize harness
    harness = TripleAgentHarness(
        model=os.getenv("TRIPLE_AGENT_MODEL", "glm-5.2"),
    )
    
    print(f"\n{'='*60}")
    print("  Triple Agent Parallel Harness — Telegram Bot")
    print(f"{'='*60}")
    print(f"  Model: {harness.model}")
    print(f"  Room:  {harness.room_dir}")
    print(f"  Logs:  {harness.log_dir}")
    print(f"\n  Agents:")
    for label, agent in harness.agents.items():
        print(f"    {AGENT_LABELS[label]} ({agent.name}) — {'room-equipped' if agent.has_room else 'no room'}")
    print(f"\n  Bot is live. Send a message to start.")
    print(f"{'='*60}\n")
    
    # Get bot info
    bot_info = requests.get(f"{API_BASE}/getMe", timeout=10).json()
    if bot_info.get("ok"):
        bot_name = bot_info["result"]["username"]
        log.info(f"Connected as @{bot_name}")
    else:
        log.error(f"Could not connect to Telegram: {bot_info}")
        return
    
    offset = None
    
    while True:
        try:
            updates = tg_get_updates(offset=offset, timeout=30)
            
            for update in updates:
                offset = update["update_id"] + 1
                
                if "message" not in update:
                    continue
                
                msg = update["message"]
                chat_id = msg["chat"]["id"]
                user_text = msg.get("text", "")
                user_name = msg.get("from", {}).get("first_name", "User")
                reply_to_msg_id = msg.get("reply_to_message", {}).get("message_id")
                msg_id = msg["message_id"]
                
                # Handle commands
                if user_text.startswith("/"):
                    cmd = user_text.lower().strip()
                    
                    if cmd == "/start" or cmd == "/help":
                        help_text = (
                            "*Triple Agent Parallel Harness*\n\n"
                            "Every message you send goes to three independent agents:\n"
                            "🅰️ *Vanilla* — no identity, no personality\n"
                            "🅱️ *Baseline* — warm, direct personality, no room\n"
                            "🏠 *Room* — full identity architecture with accumulating journal\n\n"
                            "*Reply to* a specific agent's message to talk to just that one.\n\n"
                            "Commands:\n"
                            "`/journal` — trigger room agent to write a journal entry\n"
                            "`/stats` — show session statistics\n"
                            "`/reset` — reset all conversation histories\n"
                            "`/help` — this message"
                        )
                        tg_send(chat_id, help_text, reply_to=msg_id)
                        continue
                    
                    elif cmd == "/journal":
                        tg_send(chat_id, "🏠 Room agent is reflecting...", reply_to=msg_id)
                        entry = harness.journal_room_agent()
                        tg_send(chat_id, f"*🏠 Room agent journaled:*\n\n{entry}", reply_to=msg_id)
                        continue
                    
                    elif cmd == "/stats":
                        stats = harness.get_stats()
                        stats_text = (
                            f"*Session Stats*\n\n"
                            f"Model: `{stats['model']}`\n\n"
                        )
                        for label, info in stats["agents"].items():
                            name = AGENT_LABELS.get(label, label)
                            room = "🏠 room" if info["has_room"] else "no room"
                            stats_text += f"{name} — {info['message_count']} msgs ({room})\n"
                        stats_text += f"\nRoom files: {', '.join(stats.get('room_files', []))}"
                        tg_send(chat_id, stats_text, reply_to=msg_id)
                        continue
                    
                    elif cmd == "/reset":
                        # Re-initialize harness (keeps room files on disk)
                        harness = TripleAgentHarness(
                            model=harness.model,
                            room_dir=harness.room_dir,
                            log_dir=harness.log_dir,
                        )
                        tg_send(chat_id, "✅ All conversation histories reset. Room files preserved.", reply_to=msg_id)
                        continue
                    
                    else:
                        # Unknown command — treat as regular message
                        pass
                
                # Skip empty messages
                if not user_text.strip():
                    continue
                
                log.info(f"[{user_name}] {'→ directed' if reply_to_msg_id else '→ broadcast'}: {user_text[:80]}...")
                
                # Send typing indicator
                requests.post(f"{API_BASE}/sendChatAction", json={
                    "chat_id": chat_id, "action": "typing"
                }, timeout=5)
                
                # Route to agents
                responses = harness.route_message(user_text, reply_to_msg_id)
                
                # Send responses
                is_broadcast = len(responses) > 1
                
                for label, response in responses.items():
                    agent_name = harness.agents[label].name
                    formatted = format_response(label, agent_name, response)
                    
                    # Small delay between messages for readability
                    if is_broadcast:
                        time.sleep(0.5)
                    
                    result = tg_send(chat_id, formatted, reply_to=msg_id if not is_broadcast else None)
                    
                    # Register this Telegram message_id with its agent
                    # so future replies route correctly
                    if result.get("ok"):
                        sent_msg_id = result["result"]["message_id"]
                        harness.register_response(label, sent_msg_id)
                
                elapsed_note = ""
                log.info(f"  Delivered {len(responses)} response(s)")
        
        except KeyboardInterrupt:
            log.info("Shutting down...")
            break
        except Exception as e:
            log.error(f"Error in main loop: {e}", exc_info=True)
            time.sleep(5)  # Back off on errors


if __name__ == "__main__":
    run_bot()
