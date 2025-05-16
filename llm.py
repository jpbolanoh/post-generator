"""
LLM (Language Model) module for Social-GPT.
Uses the modern OpenAI Python client directly instead of LangChain.
"""

import os
from enum import Enum
import inquirer
import openai
from openai import OpenAI
from typing import List, Dict, Any, Optional, Union


class GenerationItemType(Enum):
    """Types of content that can be generated."""
    TOPICS = 1
    IDEAS = 2
    POST = 3
    IMAGE_PROMPT = 4
    IMAGE = 5  # For direct image generation


class GenerationMode(Enum):
    """Quality settings for content generation."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    def to_string(self):
        """Convert enum to display string."""
        if self == GenerationMode.LOW:
            return "Low quality (fast + cheap)"
        if self == GenerationMode.MEDIUM:
            return "Medium quality (recommended)"
        if self == GenerationMode.HIGH:
            return "High quality (slow + expensive)"

    @staticmethod
    def get_mode_strings():
        """Get all mode strings for UI display."""
        return [
            GenerationMode.LOW.to_string(),
            GenerationMode.MEDIUM.to_string(),
            GenerationMode.HIGH.to_string(),
        ]

    @staticmethod
    def from_string(value: str):
        """Convert display string back to enum."""
        if value == "Low quality (fast + cheap)":
            return GenerationMode.LOW
        if value == "Medium quality (recommended)":
            return GenerationMode.MEDIUM
        if value == "High quality (slow + expensive)":
            return GenerationMode.HIGH


class LLM:
    """
    LLM service manager that handles model selection and content generation.
    Uses different models based on content type and quality settings.
    Uses the modern OpenAI Python client.
    """
    
    # Initialize OpenAI client
    @staticmethod
    def get_client():
        """Get initialized OpenAI client."""
        api_key = os.environ.get("OPENAI_API_KEY")
        return OpenAI(api_key=api_key)
    
    # Model mapping
    @staticmethod
    def get_model_for_type_and_mode(content_type: GenerationItemType, mode: GenerationMode) -> str:
        """
        Get the appropriate model name based on content type and quality mode.
        
        Args:
            content_type: Type of content being generated
            mode: Quality mode (LOW, MEDIUM, HIGH)
            
        Returns:
            Model name string
        """
        # Default fallback model
        model = "gpt-3.5-turbo"
        
        # For topic generation
        if content_type == GenerationItemType.TOPICS:
            if mode == GenerationMode.LOW:
                model = "gpt-3.5-turbo"
            elif mode == GenerationMode.MEDIUM:
                model = "gpt-4o-mini"
            else:  # HIGH
                model = "gpt-4o"
        
        # For idea generation
        elif content_type == GenerationItemType.IDEAS:
            if mode == GenerationMode.LOW:
                model = "gpt-3.5-turbo"
            elif mode == GenerationMode.MEDIUM:
                model = "gpt-4o-mini"
            else:  # HIGH
                model = "gpt-4o"
        
        # For post content
        elif content_type == GenerationItemType.POST:
            if mode == GenerationMode.LOW:
                model = "gpt-3.5-turbo"
            elif mode == GenerationMode.MEDIUM:
                model = "gpt-4o-mini"
            else:  # HIGH
                model = "gpt-4o"
        
        # For image prompt generation
        elif content_type == GenerationItemType.IMAGE_PROMPT:
            # Always use at least GPT-4o mini for image prompts to get good results
            if mode == GenerationMode.LOW:
                model = "gpt-4o-mini"
            else:  # MEDIUM or HIGH
                model = "gpt-4o"
                
        # For direct image generation
        elif content_type == GenerationItemType.IMAGE:
            model = "gpt-image-1"
            
        return model
    
    @staticmethod
    def generate(prompt_messages, type: GenerationItemType, mode: GenerationMode):
        """
        Generate content using the appropriate model based on content type and quality mode.
        This is a drop-in replacement for the LangChain ChatOpenAI model.
        
        Args:
            prompt_messages: List of message dictionaries for the conversation
            type: GenerationItemType enum value
            mode: GenerationMode enum value
            
        Returns:
            Message object with generated content
        """
        client = LLM.get_client()
        model = LLM.get_model_for_type_and_mode(type, mode)
        
        # Convert LangChain-style messages to OpenAI API format
        formatted_messages = []
        for message in prompt_messages:
            if hasattr(message, 'type') and message.type == 'human':
                formatted_messages.append({"role": "user", "content": message.content})
            elif hasattr(message, 'type') and message.type == 'ai':
                formatted_messages.append({"role": "assistant", "content": message.content})
            elif hasattr(message, 'type') and message.type == 'system':
                formatted_messages.append({"role": "system", "content": message.content})
            elif hasattr(message, 'role') and hasattr(message, 'content'):
                # Handle HumanMessage, AIMessage, SystemMessage from langchain.schema
                role_mapping = {
                    "human": "user",
                    "ai": "assistant",
                    "system": "system"
                }
                formatted_messages.append({
                    "role": role_mapping.get(message.role, message.role),
                    "content": message.content
                })
            else:
                # Assume it's already in the correct format
                formatted_messages.append(message)
        
        # Generate completion
        completion = client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            temperature=0.7,
        )
        
        # Create a response object similar to what LangChain would return
        return MessageResponse(completion.choices[0].message.content)

    @staticmethod
    def request_generation_mode():
        """Interactive console prompt to select generation mode."""
        return GenerationMode.from_string(inquirer.prompt([inquirer.List(
            'generation', 
            message="Which generation mode will be used?", 
            choices=GenerationMode.get_mode_strings(), 
            default=GenerationMode.MEDIUM.to_string()
        )])['generation'])


class MessageResponse:
    """
    Simple message response class to maintain compatibility with LangChain's interface.
    """
    def __init__(self, content: str):
        self.content = content
        self.type = "ai"
        
    def __call__(self, messages):
        """Make the object callable like the LangChain model."""
        return self