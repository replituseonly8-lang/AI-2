#!/usr/bin/env python3
"""
RYSTRIX AI Image Handler
Handles AI image generation with ReflexAI integration
"""

import aiohttp
import asyncio
import logging
import config

logger = logging.getLogger(__name__)

async def generate_reflexai_image(prompt: str, template: str = 'default') -> dict:
    """Generate image using ReflexAI with enhanced prompts"""
    
    # Enhance prompt based on template
    enhanced_prompt = config.PROMPT_ENHANCERS.get(template, config.PROMPT_ENHANCERS['default']).format(prompt=prompt)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                config.IMAGE_API_URL,
                json={
                    "prompt": enhanced_prompt,
                    "model": config.IMAGE_MODEL,
                    "n": 1,
                    "size": "1024x1024",
                    "quality": "hd",
                    "style": "vivid"
                },
                headers={"Content-Type": "application/json"},
                timeout=config.API_TIMEOUT
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "image_url": data["data"][0]["url"],
                        "enhanced_prompt": enhanced_prompt
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"ReflexAI Image API error {response.status}: {error_text}")
                    return {
                        "success": False,
                        "error": "Image service is currently unavailable. Please try again later."
                    }
    except asyncio.TimeoutError:
        logger.error("ReflexAI Image API timeout")
        return {
            "success": False,
            "error": "Request timeout. The image generation is taking too long."
        }
    except aiohttp.ClientError as e:
        logger.error(f"ReflexAI Image API connection error: {e}")
        return {
            "success": False,
            "error": "Connection error. Please check your network."
        }
    except Exception as e:
        logger.error(f"ReflexAI Image API unexpected error: {e}")
        return {
            "success": False,
            "error": f"Processing error: {str(e)}"
        }

def detect_image_template(prompt: str) -> str:
    """Detect the best template based on prompt content"""
    prompt_lower = prompt.lower()
    
    if any(word in prompt_lower for word in ["portrait", "face", "person", "headshot"]):
        return 'portrait'
    elif any(word in prompt_lower for word in ["landscape", "scenery", "mountain", "ocean", "sunset", "nature"]):
        return 'landscape'
    elif any(word in prompt_lower for word in ["anime", "cartoon", "manga", "chibi", "kawaii"]):
        return 'anime'
    elif any(word in prompt_lower for word in ["realistic", "photo", "photorealistic", "real", "lifelike"]):
        return 'realistic'
    else:
        return 'default'

async def process_image_generation(prompt: str) -> dict:
    """Process image generation request"""
    
    try:
        # Validate prompt
        if not prompt or len(prompt.strip()) < 3:
            return {
                "success": False,
                "error": "Please provide a more detailed prompt for better results."
            }
        
        if len(prompt) > 1000:
            return {
                "success": False,
                "error": "Prompt is too long. Please keep it under 1000 characters."
            }
        
        # Detect template
        template = detect_image_template(prompt)
        
        # Generate image
        result = await generate_reflexai_image(prompt, template)
        
        if result["success"]:
            result["template_used"] = template
            result["original_prompt"] = prompt
        
        return result
        
    except Exception as e:
        logger.error(f"Image processing error: {e}")
        return {
            "success": False,
            "error": "Processing error. Please try again."
        }

def get_image_tips() -> str:
    """Get tips for better image generation"""
    return (
        "**💡 Tips for Better Images:**\n"
        "• Be specific with details (colors, style, mood)\n"
        "• Mention art style (realistic, anime, cartoon)\n"
        "• Include lighting preferences (bright, dark, sunset)\n"
        "• Describe composition (close-up, wide shot)\n"
        "• Add quality terms (high quality, detailed, 4k)\n\n"
        "**🎨 Available Styles:**\n"
        "• Realistic/Photo - for lifelike images\n"
        "• Anime/Manga - for Japanese animation style\n"
        "• Portrait - for face and character focus\n"
        "• Landscape - for scenic and nature views"
    )

def get_example_prompts() -> list:
    """Get example prompts for inspiration"""
    return [
        "a majestic dragon flying over a medieval castle at sunset",
        "anime girl with blue hair in a cyberpunk city",
        "realistic portrait of a wise old wizard with a long beard",
        "beautiful landscape with mountains reflected in a crystal lake",
        "futuristic robot in a neon-lit laboratory",
        "cute cat wearing a detective hat, cartoon style",
        "epic space battle with starships and nebula background",
        "serene Japanese garden with cherry blossoms falling"
    ]