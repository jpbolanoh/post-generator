"""
Image Generation Module for Social-GPT using OpenAI's GPT-image-1 model.
"""

import os
import time
import requests
import io
from PIL import Image
from datetime import datetime
import openai
from logger import Logger
from utils import count_files_in_directory
from llm import LLM, GenerationMode

def analyze_image_complexity(prompt: str) -> str:
    """
    Analyze the complexity of an image request.
    
    Args:
        prompt: The image generation prompt
        
    Returns:
        Complexity level: "low", "medium", or "high"
    """
    # Count keywords that suggest complexity
    complexity_terms = [
        "detailed", "intricate", "complex", "multiple", "scene", 
        "realistic", "photorealistic", "high-quality", "specific layout",
        "particular arrangement", "precise", "exact", "photorealistic", 
        "perspective", "angle", "composition"
    ]
    
    # Count how many complexity indicators are in the prompt
    count = sum(1 for term in complexity_terms if term.lower() in prompt.lower())
    
    # Determine complexity level
    if count <= 2:
        return "low"
    elif count <= 5:
        return "medium"
    else:
        return "high"

def generate_image_with_openai(
    prompt: str, 
    generation_mode: GenerationMode = GenerationMode.MEDIUM,
    model_preference: str = "GPT-image-1",
    size: str = "1024x1024",
    quality: str = "standard"
) -> str:
    """
    Generate an image using OpenAI's GPT-image-1 model.
    
    Args:
        prompt: The text prompt to use for generating the image
        generation_mode: Quality setting for generation
        model_preference: Which model to use (always uses GPT-image-1)
        size: Image dimensions
        quality: Image quality setting
        
    Returns:
        str: Path to the saved image
    """
    try:
        # Make sure the OpenAI API key is set
        if not openai.api_key:
            openai.api_key = os.environ.get("OPENAI_API_KEY")
            
        if not openai.api_key:
            raise ValueError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")
        
        # Analyze prompt complexity for logging purposes
        complexity = analyze_image_complexity(prompt)
        
        # For GPT-image-1 model
        Logger.log("Image Generation", f"Using GPT-image-1 for image generation (complexity: {complexity})")
        
        # Set quality based on parameter or generation mode
        if quality not in ["standard", "hd"]:
            quality = "hd" if generation_mode == GenerationMode.HIGH else "standard"
        
        # Create a response using GPT-image-1
        response = openai.images.generate(
            model="dall-e-3",  # Specify GPT-image-1 model
            prompt=prompt,
            size=size,  # Use the specified size
            quality=quality,
            n=1,  # Number of images to generate
        )
        
        # Get the image URL
        image_url = response.data[0].url
        
        # Download the image
        image_response = requests.get(image_url)
        if image_response.status_code != 200:
            raise Exception(f"Failed to download image: {image_response.status_code}")
        
        image_content = image_response.content
        
        # Save the image
        existing_images = count_files_in_directory("results/images")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"post_{existing_images + 1}_{timestamp}.png"
        filepath = f"results/images/{filename}"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save the image
        with open(filepath, 'wb') as f:
            f.write(image_content)
        
        # Log the success
        Logger.log(f"Generated Image", f"Filename: {filename}\nPrompt: {prompt}")
        
        return filepath
    
    except Exception as e:
        Logger.log("Error generating image", str(e))
        raise e

def generate_image_with_hf(prompt: str) -> str:
    """
    Legacy function for HuggingFace image generation.
    Now redirects to OpenAI GPT-image-1 generation.
    """
    return generate_image_with_openai(prompt)