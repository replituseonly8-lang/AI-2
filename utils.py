#!/usr/bin/env python3
"""
RYSTRIX AI Utilities
Common utilities and helper functions for the Telegram bot
"""

import asyncio
import logging
from telebot import types
import config

logger = logging.getLogger(__name__)

def main_keyboard():
    """Create main menu inline keyboard"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("💬 Chat Mode", callback_data="chat_mode"),
        types.InlineKeyboardButton("🖼️ Generate Image", callback_data="image_gen")
    )
    keyboard.add(
        types.InlineKeyboardButton("🔊 Text-to-Speech", callback_data="tts"),
        types.InlineKeyboardButton("❓ Help", callback_data="help")
    )
    return keyboard

def chat_mode_keyboard():
    """Create chat mode keyboard"""
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🚪 Exit Chat Mode", callback_data="exit_chat"))
    return keyboard

def back_keyboard():
    """Create back to main menu keyboard"""
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_main"))
    return keyboard

def admin_keyboard():
    """Create admin-only keyboard"""
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("📊 Statistics", callback_data="admin_stats"),
        types.InlineKeyboardButton("🔄 Restart", callback_data="admin_restart")
    )
    keyboard.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_main"))
    return keyboard

async def animated_thinking(bot, message):
    """Animate thinking dots"""
    thinking_states = [
        f"🤔 **{config.BOT_NAME} is thinking**.",
        f"🤔 **{config.BOT_NAME} is thinking**..",
        f"🤔 **{config.BOT_NAME} is thinking**...",
        "🧠 **Processing your request**.",
        "🧠 **Processing your request**..",
        "🧠 **Processing your request**...",
        "⚡ **Generating response**.",
        "⚡ **Generating response**..",
        "⚡ **Generating response**..."
    ]
    
    try:
        while True:
            for state in thinking_states:
                try:
                    await bot.edit_message_text(
                        state,
                        message.chat.id,
                        message.message_id,
                        parse_mode="Markdown"
                    )
                    await asyncio.sleep(0.8)
                except Exception:
                    return
    except asyncio.CancelledError:
        pass

async def animated_imaging(bot, message):
    """Animate image generation status"""
    imaging_states = [
        "🎨 **Creating your image**.",
        "🎨 **Creating your image**..",
        "🎨 **Creating your image**...",
        "🖼️ **Rendering artwork**.",
        "🖼️ **Rendering artwork**..",
        "🖼️ **Rendering artwork**...",
        "✨ **Adding final touches**.",
        "✨ **Adding final touches**..",
        "✨ **Adding final touches**..."
    ]
    
    try:
        while True:
            for state in imaging_states:
                try:
                    await bot.edit_message_text(
                        state,
                        message.chat.id,
                        message.message_id,
                        parse_mode="Markdown"
                    )
                    await asyncio.sleep(1.0)
                except Exception:
                    return
    except asyncio.CancelledError:
        pass

async def animated_tts(bot, message):
    """Animate TTS generation status"""
    tts_states = [
        "🔊 **Converting text to speech**.",
        "🔊 **Converting text to speech**..",
        "🔊 **Converting text to speech**...",
        "🎵 **Processing audio**.",
        "🎵 **Processing audio**..",
        "🎵 **Processing audio**...",
        "🎧 **Preparing voice**.",
        "🎧 **Preparing voice**..",
        "🎧 **Preparing voice**..."
    ]
    
    try:
        while True:
            for state in tts_states:
                try:
                    await bot.edit_message_text(
                        state,
                        message.chat.id,
                        message.message_id,
                        parse_mode="Markdown"
                    )
                    await asyncio.sleep(0.7)
                except Exception:
                    return
    except asyncio.CancelledError:
        pass

def format_uptime(uptime_delta):
    """Format uptime delta into readable string"""
    days = uptime_delta.days
    hours, remainder = divmod(uptime_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)

def validate_user_input(text, max_length=1000, min_length=1):
    """Validate user input text"""
    if not text or not isinstance(text, str):
        return False, "Invalid input"
    
    text = text.strip()
    if len(text) < min_length:
        return False, f"Input too short (minimum {min_length} characters)"
    
    if len(text) > max_length:
        return False, f"Input too long (maximum {max_length} characters)"
    
    return True, text

def is_admin(user_id):
    """Check if user is admin"""
    return user_id == config.ADMIN_ID

def get_user_info(user):
    """Extract user information safely"""
    return {
        "id": user.id,
        "first_name": getattr(user, 'first_name', 'Unknown'),
        "last_name": getattr(user, 'last_name', ''),
        "username": getattr(user, 'username', ''),
        "full_name": f"{getattr(user, 'first_name', 'Unknown')} {getattr(user, 'last_name', '')}".strip()
    }

def escape_markdown(text):
    """Escape special markdown characters"""
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

def truncate_text(text, max_length=100, suffix="..."):
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

async def send_typing_action(bot, chat_id, duration=2):
    """Send typing action for specified duration"""
    try:
        await bot.send_chat_action(chat_id, 'typing')
        await asyncio.sleep(duration)
    except Exception as e:
        logger.error(f"Error sending typing action: {e}")

def create_progress_bar(current, total, length=10):
    """Create a simple progress bar"""
    filled = int(length * current / total)
    bar = "█" * filled + "░" * (length - filled)
    percentage = int(100 * current / total)
    return f"{bar} {percentage}%"

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"