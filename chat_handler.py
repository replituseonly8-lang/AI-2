import aiohttp
import asyncio
import shared
from utils import animated_thinking, back_keyboard
from telegram.constants import ParseMode
import re
import urllib.parse
import config

def validate_markdown(text):
    """Ensure proper Markdown formatting"""
    text = text.replace("** ", "**").replace(" **", "**")
    text = re.sub(r"\*\*(.+?)\*\*", r"**\1**", text)
    return text

async def generate_gpt4_text(prompt: str) -> str:
    async with aiohttp.ClientSession() as sess:
        async with sess.post(
            config.CHAT_API_URL,
            json={
                "model": config.CHAT_MODEL,
                "messages": [
                    {"role": "system", "content": config.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=config.API_TIMEOUT
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data["choices"][0]["message"]["content"]

async def process_chat(text, thinking_msg, uid):
    think_task = asyncio.create_task(animated_thinking(thinking_msg))
    
    try:
        if uid not in shared.user_conversations:
            shared.user_conversations[uid] = []

        # Call GPT-4 AI for text
        reply = await generate_gpt4_text(text)

        # Validate Markdown
        reply = validate_markdown(reply)

        # Store in conversation history
        shared.user_conversations[uid].append({"role": "user", "content": text})
        shared.user_conversations[uid].append({"role": "assistant", "content": reply})

        if len(shared.user_conversations[uid]) > 10:
            shared.user_conversations[uid] = shared.user_conversations[uid][-10:]

    except (aiohttp.ClientError, asyncio.TimeoutError):
        reply = "⚠️ Connection error. Please check your network."
    except Exception as e:
        reply = f"⚠️ Processing error: {str(e)}"
    
    think_task.cancel()

    await thinking_msg.edit_text(
        f"💬 Bot:\n\n{reply.strip()}\n\n",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=back_keyboard()
    )
