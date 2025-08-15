#!/usr/bin/env python3
"""
RYSTRIX AI Telegram Bot
A comprehensive Telegram bot with AI chat, image generation, and TTS capabilities.
"""

import logging
import asyncio
import aiohttp
import time
import json
from datetime import datetime
import telebot
from telebot import types
from telebot.async_telebot import AsyncTeleBot
import config
from chat_handler import process_chat as handle_chat

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize bot
bot = AsyncTeleBot(config.BOT_TOKEN)

# User data storage
user_conversations = {}
chat_mode_users = set()

# Bot start time for uptime calculation
bot_start_time = datetime.now()

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

@bot.message_handler(commands=['start'])
async def start_command(message):
    """Handle /start command"""
    user = message.from_user
    welcome_message = (
        f"🤖 **Welcome to {config.BOT_NAME}**, {user.first_name}!\n\n"
        "🚀 **Your AI-Powered Assistant**\n\n"
        "✨ **Features:**\n"
        "💬 **Smart Chat** - Intelligent conversations with advanced AI\n"
        "🖼️ **Image Creation** - Generate stunning artwork and visuals\n"
        "🔊 **Voice Synthesis** - High-quality text-to-speech conversion\n"
        "⚡ **Chat Mode** - Seamless conversation experience\n\n"
        "🎯 **Available Commands:**\n"
        "• `/chat` - Enter interactive chat mode\n"
        "• `/image <prompt>` - Create custom images\n"
        "• `/say <text>` - Convert text to speech\n"
        "• `/ping` - Check system status & performance\n"
        "• `/help` - Get detailed help information\n\n"
        f"🏆 **{config.BOT_VERSION}** | Powered by Advanced AI Technology\n"
        f"👨‍💻 **Developer:** {config.DEVELOPER_HANDLE}\n"
        f"🌟 **Community:** {config.COMMUNITY_HANDLE}\n\n"
        "**Ready to assist you 24/7!**"
    )
    
    keyboard = main_keyboard()
    await bot.send_message(
        message.chat.id,
        welcome_message,
        parse_mode='Markdown',
        reply_markup=keyboard
    )

@bot.message_handler(commands=['help'])
async def help_command(message):
    """Handle /help command"""
    help_text = (
        f"🤖 **{config.BOT_NAME} Help**\n\n"
        "**🔧 Commands:**\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/chat - Enter chat mode for conversations\n"
        "/image <prompt> - Generate an image\n"
        "/say <text> - Convert text to speech\n"
        "/ping - Check bot status and uptime\n\n"
        "**💡 Tips:**\n"
        "• Use Chat Mode for cleaner conversations\n"
        "• Be specific with image prompts for better results\n"
        "• TTS supports multiple languages\n\n"
        f"**📞 Support:** {config.COMMUNITY_HANDLE}"
    )
    
    keyboard = main_keyboard()
    await bot.send_message(
        message.chat.id,
        help_text,
        parse_mode='Markdown',
        reply_markup=keyboard
    )

@bot.message_handler(commands=['ping'])
async def ping_command(message):
    """Handle /ping command"""
    start_time = time.time()
    
    # Calculate uptime
    uptime = datetime.now() - bot_start_time
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    # Send initial message
    msg = await bot.send_message(
        message.chat.id,
        "🏃‍♂️ **Checking status...**",
        parse_mode='Markdown'
    )
    
    # Calculate response time
    response_time = (time.time() - start_time) * 1000
    
    # Test API connectivity
    api_status = "✅ Online"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{config.API_BASE_URL}/models", timeout=5) as response:
                if response.status != 200:
                    api_status = "⚠️ Degraded"
    except:
        api_status = "❌ Offline"
    
    ping_message = (
        "🏓 **Bot Status**\n\n"
        f"📊 **Response Time:** {response_time:.0f}ms\n"
        f"⏱️ **Uptime:** {days}d {hours}h {minutes}m {seconds}s\n"
        f"🔗 **API Status:** {api_status}\n"
        f"👥 **Active Users:** {len(user_conversations)}\n"
        f"🤖 **Bot Version:** {config.BOT_VERSION}\n\n"
        f"Made by {config.DEVELOPER_HANDLE}"
    )
    
    keyboard = main_keyboard()
    await bot.edit_message_text(
        ping_message,
        message.chat.id,
        msg.message_id,
        parse_mode='Markdown',
        reply_markup=keyboard
    )

@bot.message_handler(commands=['chat'])
async def chat_command(message):
    """Handle /chat command - enter chat mode"""
    user_id = message.from_user.id
    chat_mode_users.add(user_id)
    
    keyboard = chat_mode_keyboard()
    await bot.send_message(
        message.chat.id,
        "💬 **Chat Mode Activated!**\n\n"
        f"Now you can chat directly with {config.BOT_NAME}. Just send your messages!\n"
        "Use the 'Exit Chat Mode' button below to return to main menu.",
        parse_mode='Markdown',
        reply_markup=keyboard
    )

@bot.message_handler(commands=['image'])
async def image_command(message):
    """Handle /image command"""
    # Extract prompt from message
    command_parts = message.text.split(' ', 1)
    if len(command_parts) < 2:
        keyboard = main_keyboard()
        await bot.send_message(
            message.chat.id,
            "🖼️ **Image Generation**\n\n"
            "Please provide a prompt:\n"
            "`/image your prompt here`\n\n"
            "**Examples:**\n"
            "• `/image a beautiful sunset over mountains`\n"
            "• `/image anime girl with blue hair`\n"
            "• `/image realistic portrait of a cat`",
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        return
    
    prompt = command_parts[1]
    status_msg = await bot.send_message(
        message.chat.id,
        "🎨 **Generating image...**\n\nThis may take a moment.",
        parse_mode='Markdown'
    )
    
    await process_image_generation(prompt, status_msg, message, message.from_user.id)

@bot.message_handler(commands=['say'])
async def say_command(message):
    """Handle /say command - Text to Speech"""
    # Extract text from message
    command_parts = message.text.split(' ', 1)
    if len(command_parts) < 2:
        keyboard = main_keyboard()
        await bot.send_message(
            message.chat.id,
            "🔊 **Text-to-Speech**\n\n"
            "Please provide text to convert:\n"
            "`/say your text here`\n\n"
            "**Examples:**\n"
            f"• `/say Hello, this is {config.BOT_NAME}!`\n"
            "• `/say Welcome to our community`",
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        return
    
    text = command_parts[1]
    
    if len(text) > 1000:
        keyboard = main_keyboard()
        await bot.send_message(
            message.chat.id,
            "⚠️ **Text too long!**\n\nPlease keep your text under 1000 characters.",
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        return
    
    status_msg = await bot.send_message(
        message.chat.id,
        "🔊 **Generating speech...**\n\nProcessing your text...",
        parse_mode='Markdown'
    )
    
    await process_tts_generation(text, status_msg, message)

async def process_tts_generation(text, status_msg, message):
    """Process TTS generation"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                config.TTS_API_URL,
                json={
                    "model": config.TTS_MODEL,
                    "input": text,
                    "voice": "aria",
                    "response_format": "mp3"
                },
                timeout=config.API_TIMEOUT
            ) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    
                    await bot.send_voice(
                        message.chat.id,
                        audio_data,
                        caption=f"🔊 **TTS Generated**\n\n📝 **Text:** {text[:100]}{'...' if len(text) > 100 else ''}\n\n`{config.UNIQUE_WORD}`",
                        parse_mode='Markdown',
                        reply_to_message_id=message.message_id
                    )
                    await bot.delete_message(message.chat.id, status_msg.message_id)
                else:
                    keyboard = main_keyboard()
                    await bot.edit_message_text(
                        "⚠️ **TTS service unavailable**\n\nPlease try again later.",
                        message.chat.id,
                        status_msg.message_id,
                        parse_mode='Markdown',
                        reply_markup=keyboard
                    )
    except asyncio.TimeoutError:
        keyboard = main_keyboard()
        await bot.edit_message_text(
            "⚠️ **Request timeout**\n\nThe text was too long or service is slow.",
            message.chat.id,
            status_msg.message_id,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"TTS error: {e}")
        keyboard = main_keyboard()
        await bot.edit_message_text(
            "⚠️ **TTS generation failed**\n\nPlease try again or contact support.",
            message.chat.id,
            status_msg.message_id,
            parse_mode='Markdown',
            reply_markup=keyboard
        )

async def process_image_generation(text, status_msg, message, uid):
    """Process image generation"""
    imaging_task = asyncio.create_task(animate_imaging(status_msg))
    
    try:
        prompt_lower = text.lower()
        template = 'default'
        
        if "portrait" in prompt_lower or "face" in prompt_lower:
            template = 'portrait'
        elif "landscape" in prompt_lower or "scenery" in prompt_lower:
            template = 'landscape'
        elif "anime" in prompt_lower or "cartoon" in prompt_lower:
            template = 'anime'
        elif "realistic" in prompt_lower or "photo" in prompt_lower:
            template = 'realistic'
        
        enhanced_prompt = config.PROMPT_ENHANCERS[template].format(prompt=text)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                config.IMAGE_API_URL,
                json={
                    "prompt": enhanced_prompt,
                    "model": config.IMAGE_MODEL,
                    "n": 1,
                    "size": "1024x1024",
                    "quality": "hd"
                },
                timeout=config.API_TIMEOUT
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    image_url = data["data"][0]["url"]
                    
                    await bot.send_photo(
                        message.chat.id,
                        image_url,
                        caption=f"🖼️ **Generated Image**\n\n📝 **Prompt:** {text}\n\n`{config.UNIQUE_WORD}`",
                        parse_mode='Markdown',
                        reply_to_message_id=message.message_id
                    )
                    await bot.delete_message(message.chat.id, status_msg.message_id)
                else:
                    await bot.edit_message_text(
                        "⚠️ Image service is busy. Please try again later.",
                        message.chat.id,
                        status_msg.message_id
                    )
    except (aiohttp.ClientError, asyncio.TimeoutError):
        await bot.edit_message_text(
            "⚠️ Connection to image service failed.",
            message.chat.id,
            status_msg.message_id
        )
    except Exception as e:
        await bot.edit_message_text(
            f"⚠️ Failed to generate image: {str(e)}",
            message.chat.id,
            status_msg.message_id
        )
    finally:
        imaging_task.cancel()



async def process_chat_message(text, thinking_msg, uid):
    """Process chat message and generate AI response"""
    from chat_handler import process_chat_message as handle_chat
    
    think_task = asyncio.create_task(animate_thinking(thinking_msg))
    
    try:
        # Use the dedicated chat handler
        reply = await handle_chat(text, thinking_msg, user_id)
        
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        reply = "⚠️ Processing error. Please try again."
    
    think_task.cancel()

    keyboard = back_keyboard()
    await bot.edit_message_text(
        f"💬 **{config.BOT_NAME}:**\n\n{reply.strip()}\n\n",
        thinking_msg.chat.id,
        thinking_msg.message_id,
        parse_mode='Markdown',
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: True)
async def handle_callback_query(call):
    """Handle inline keyboard callbacks"""
    await bot.answer_callback_query(call.id)
    
    user_id = call.from_user.id
    message = call.message
    
    if call.data == "chat_mode":
        chat_mode_users.add(user_id)
        keyboard = chat_mode_keyboard()
        await bot.edit_message_text(
            "💬 **Chat Mode Activated!**\n\n"
            f"Now you can chat directly with {config.BOT_NAME}. Just send your messages!\n"
            "Use the 'Exit Chat Mode' button below to return to main menu.",
            message.chat.id,
            message.message_id,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    
    elif call.data == "exit_chat":
        chat_mode_users.discard(user_id)
        keyboard = main_keyboard()
        await bot.edit_message_text(
            "👋 **Chat Mode Deactivated**\n\n"
            f"You've exited chat mode. Use the buttons below to interact with {config.BOT_NAME}.",
            message.chat.id,
            message.message_id,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    
    elif call.data == "image_gen":
        keyboard = back_keyboard()
        await bot.edit_message_text(
            "🖼️ **Image Generation**\n\n"
            "Use the command: `/image your prompt here`\n\n"
            "**Tips for better results:**\n"
            "• Be specific and descriptive\n"
            "• Mention style (realistic, anime, cartoon)\n"
            "• Include lighting and mood details",
            message.chat.id,
            message.message_id,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    
    elif call.data == "tts":
        keyboard = back_keyboard()
        await bot.edit_message_text(
            "🔊 **Text-to-Speech**\n\n"
            "Use the command: `/say your text here`\n\n"
            "**Features:**\n"
            "• High-quality voice synthesis\n"
            "• Multiple language support\n"
            "• Fast processing",
            message.chat.id,
            message.message_id,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    
    elif call.data == "help":
        keyboard = back_keyboard()
        await bot.edit_message_text(
            f"🤖 **{config.BOT_NAME} Help**\n\n"
            "**🔧 Commands:**\n"
            "/start - Start the bot\n"
            "/help - Show help message\n"
            "/chat - Enter chat mode\n"
            "/image <prompt> - Generate image\n"
            "/say <text> - Text-to-speech\n"
            "/ping - Bot status\n\n"
            f"**📞 Support:** {config.COMMUNITY_HANDLE}",
            message.chat.id,
            message.message_id,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    
    elif call.data == "back_main":
        keyboard = main_keyboard()
        await bot.edit_message_text(
            f"🤖 **{config.BOT_NAME}**\n\n"
            "Your intelligent assistant for chat, image generation, and text-to-speech!\n\n"
            "Choose an option below to get started:",
            message.chat.id,
            message.message_id,
            parse_mode='Markdown',
            reply_markup=keyboard
        )

@bot.message_handler(func=lambda message: True)
async def handle_message(message):
    """Handle regular messages"""
    user_id = message.from_user.id
    text = message.text
    
    # Check if user is in chat mode
    if user_id in chat_mode_users:
        thinking_msg = await bot.send_message(
            message.chat.id,
            f"🤔 **{config.BOT_NAME} is thinking...**",
            parse_mode='Markdown'
        )
        await process_chat_message(text, thinking_msg, user_id)
    else:
        # Not in chat mode, show main menu
        keyboard = main_keyboard()
        await bot.send_message(
            message.chat.id,
            f"🤖 **{config.BOT_NAME}**\n\n"
            "Please use the buttons below or commands to interact with me!\n\n"
            "💡 **Tip:** Use `/chat` to enter chat mode for direct conversations.",
            parse_mode='Markdown',
            reply_markup=keyboard
        )

async def animate_thinking(message):
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

async def animate_imaging(message):
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

async def setup_commands():
    """Setup bot commands menu"""
    commands = [
        types.BotCommand("start", "Start the bot"),
        types.BotCommand("help", "Show help message"),
        types.BotCommand("chat", "Enter chat mode"),
        types.BotCommand("image", "Generate an image"),
        types.BotCommand("say", "Text-to-speech"),
        types.BotCommand("ping", "Check bot status"),
    ]
    await bot.set_my_commands(commands)

async def main():
    """Main function to run the bot"""
    # Setup commands
    await setup_commands()
    
    logger.info(f"🚀 {config.BOT_NAME} Bot is starting...")
    logger.info(f"👑 Admin ID: {config.ADMIN_ID}")
    logger.info(f"🔗 API Base URL: {config.API_BASE_URL}")
    
    # Run the bot
    await bot.polling(non_stop=True)

if __name__ == "__main__":
    asyncio.run(main())