"""Tweet Generator for Social-GPT using modern OpenAI API."""
from utils import add_item_to_file
from prompts import Prompts
from brands import Brand
from files import Files
from logger import Logger
from llm import LLM, GenerationMode, GenerationItemType


class TweetGenerator:
    def __init__(self, brand: Brand, language: str, idea: str, prompt_expansion: str, generation_mode: GenerationMode):
        self.brand = brand
        self.language = language
        self.idea = idea
        self.prompt_expansion = prompt_expansion
        self.generation_mode = generation_mode

    def generate_tweet(self):
        """
        Generate a tweet based on the given idea and brand guidelines.
        
        Returns:
            str: The generated tweet content
        """
        # Build the system prompt with brand description
        system_prompt = {
            "role": "system",
            "content": f"""Eres un experto en crear tweets efectivos y atractivos para marcas. 
Vas a crear contenido para la siguiente marca:
{self.brand.description}

IMPORTANTE: Si la idea o las instrucciones del usuario mencionan promocionar un producto o servicio específico, 
tu tweet DEBE enfocarse directamente en promocionar ese producto/servicio y sus beneficios principales.
"""
        }
        
        # Build the user prompt with language, idea, and brand style
        prompt = f"""Escribe un tweet en {self.language} para la cuenta que trata sobre esta idea específica:
'{self.idea}'

El tweet debe:
1. Ser conciso y efectivo (máximo 280 caracteres)
2. Incluir un mensaje claro y un llamado a la acción cuando sea apropiado
3. Ser atractivo y relevante para la audiencia objetivo
4. Representar fielmente la voz de la marca{Prompts.get_avoids()}{Prompts.build_style_prompt(self.brand.style)}"""

        if self.prompt_expansion:
            prompt = prompt + f"\n\nInstrucciones adicionales (MUY IMPORTANTES): {self.prompt_expansion}"
        
        user_prompt = {
            "role": "user",
            "content": prompt
        }
        
        # Generate tweet using the LLM
        response = LLM.generate(
            [system_prompt, user_prompt],
            GenerationItemType.POST,
            self.generation_mode
        )
        
        # Extract the tweet content
        tweet = response.content.strip()
        
        # Log the result
        Logger.log("Tweet generado", tweet)
        
        # Save to file
        add_item_to_file(Files.twitter_results, tweet)
        
        return tweet