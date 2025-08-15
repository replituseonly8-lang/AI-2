"""
Configuration file for RYSTRIX AI Telegram Bot
"""

# Bot Configuration
BOT_TOKEN = "8233959472:AAENEqqWtCtPamfshy9b8rxBIsVks99tXAU"
ADMIN_ID = 7673097445

# API Configuration
API_BASE_URL = "https://reflexai-j0ro.onrender.com/v1"
CHAT_API_URL = "https://reflexai-j0ro.onrender.com/v1/chat/completions"
IMAGE_API_URL = "https://reflexai-j0ro.onrender.com/v1/images/generate"
TTS_API_URL = "https://reflexai-j0ro.onrender.com/v1/audio/speech"

# Model Configuration
CHAT_MODEL = "gpt-4"
IMAGE_MODEL = "StabilityAI_SD35Large"
TTS_MODEL = "gpt-4o-mini-tts"

# Bot Settings
UNIQUE_WORD = "🚀 By • @RytstrixHub"
API_TIMEOUT = 30
MAX_CONVERSATION_HISTORY = 10

# Bot Information
BOT_NAME = "RYSTRIX AI"
BOT_VERSION = "v2.0"
DEVELOPER_HANDLE = "@Rystrix"
COMMUNITY_HANDLE = "@RystrixHub"

# Prompt Templates for Image Generation
PROMPT_ENHANCERS = {
    'default': "{prompt}, high quality, detailed, 4k resolution",
    'portrait': "{prompt}, portrait photography, professional lighting, high resolution, detailed features",
    'landscape': "{prompt}, landscape photography, golden hour lighting, scenic, high detail, 4k",
    'anime': "{prompt}, anime style, vibrant colors, detailed illustration, high quality artwork",
    'realistic': "{prompt}, photorealistic, professional photography, high detail, 4k resolution, natural lighting"
}

# System Prompt for Chat
SYSTEM_PROMPT = (
    "You are RYSTRIX AI, a helpful, friendly, and witty Telegram assistant. "
    "Use stylish fonts and sometimes emoji. Sometimes write big paragraphs but "
    "clear and understanding. Send text as Telegram supports with proper formatting. "
    "Use bold texts and copyable text when needed."
)
