#!/usr/bin/env python3
"""
RYSTRIX AI Shared Data
Shared variables and state management for the Telegram bot
"""

import threading
from typing import Dict, Set, Any

# Thread-safe storage for user data
_lock = threading.Lock()

# User conversation histories
user_conversations: Dict[int, list] = {}

# Users currently in chat mode
chat_mode_users: Set[int] = set()

# Bot statistics
bot_stats = {
    "total_messages": 0,
    "total_images": 0,
    "total_tts": 0,
    "active_users": set(),
    "errors": 0
}

def add_conversation(user_id: int, role: str, content: str):
    """Thread-safe way to add conversation"""
    with _lock:
        if user_id not in user_conversations:
            user_conversations[user_id] = []
        
        user_conversations[user_id].append({
            "role": role,
            "content": content
        })
        
        # Keep only last 20 messages (10 exchanges)
        if len(user_conversations[user_id]) > 20:
            user_conversations[user_id] = user_conversations[user_id][-20:]

def get_conversation(user_id: int) -> list:
    """Thread-safe way to get conversation history"""
    with _lock:
        return user_conversations.get(user_id, []).copy()

def clear_conversation(user_id: int):
    """Thread-safe way to clear conversation"""
    with _lock:
        if user_id in user_conversations:
            del user_conversations[user_id]

def add_chat_mode_user(user_id: int):
    """Add user to chat mode"""
    with _lock:
        chat_mode_users.add(user_id)

def remove_chat_mode_user(user_id: int):
    """Remove user from chat mode"""
    with _lock:
        chat_mode_users.discard(user_id)

def is_in_chat_mode(user_id: int) -> bool:
    """Check if user is in chat mode"""
    with _lock:
        return user_id in chat_mode_users

def update_stats(stat_type: str, user_id: int = None):
    """Update bot statistics"""
    with _lock:
        if stat_type in bot_stats:
            if isinstance(bot_stats[stat_type], int):
                bot_stats[stat_type] += 1
            elif isinstance(bot_stats[stat_type], set) and user_id:
                bot_stats[stat_type].add(user_id)

def get_stats() -> dict:
    """Get current bot statistics"""
    with _lock:
        stats_copy = bot_stats.copy()
        # Convert sets to counts for JSON serialization
        for key, value in stats_copy.items():
            if isinstance(value, set):
                stats_copy[key] = len(value)
        return stats_copy

def reset_stats():
    """Reset all statistics"""
    with _lock:
        bot_stats["total_messages"] = 0
        bot_stats["total_images"] = 0
        bot_stats["total_tts"] = 0
        bot_stats["active_users"] = set()
        bot_stats["errors"] = 0