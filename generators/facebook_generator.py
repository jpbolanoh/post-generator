"""Facebook Generator for Social-GPT using modern OpenAI API."""
from utils import add_item_to_file
from prompts import Prompts
from brands import Brand
from files import Files
from logger import Logger
from llm import LLM, GenerationMode, GenerationItemType


class FacebookGenerator:
    def __init__(self, brand: Brand, language: str, idea: str, prompt_expansion: str, generation_mode: GenerationMode):
        self.brand = brand
        self.language = language
        self.idea = idea
        self.prompt_expansion = prompt_expansion
        self.generation_mode = generation_mode

    def generate_post(self):
        """
        Generate a Facebook post based on the given idea and brand guidelines.
        
        Returns:
            str: The generated Facebook post content
        """
        # Build the system prompt with brand description
        system_prompt = {
            "role": "system",
            "content": f"""Eres un experto en crear posts efectivos para Facebook que generan engagement y conversiones.
Vas a crear contenido para la siguiente marca:
{self.brand.description}

IMPORTANTE: Si la idea o las instrucciones del usuario mencionan promocionar un producto o servicio específico, 
tu post DEBE enfocarse directamente en promocionar ese producto/servicio, destacando sus características principales,
beneficios únicos y valor para el cliente.
"""
        }
        
        # Build the user prompt with language, idea, and brand style
        prompt = f"""Escribe un post de Facebook con 3-6 párrafos en {self.language} que trate sobre esta idea específica:
'{self.idea}'

El post debe:
1. Tener una introducción atractiva que capte la atención
2. Desarrollar la idea principal con información relevante
3. Incluir un llamado a la acción claro al final
4. Usar un tono y estilo coherente con la identidad de la marca
5. Estar optimizado para generar engagement (comentarios, compartidos, etc.){Prompts.get_avoids()}{Prompts.build_style_prompt(self.brand.style)}"""

        if self.prompt_expansion:
            prompt = prompt + f"\n\nInstrucciones adicionales (MUY IMPORTANTES): {self.prompt_expansion}"
        
        user_prompt = {
            "role": "user",
            "content": prompt
        }
        
        # Generate post using the LLM
        response = LLM.generate(
            [system_prompt, user_prompt],
            GenerationItemType.POST,
            self.generation_mode
        )
        
        # Extract the post content
        post = response.content.strip()
        
        # Log the result
        Logger.log("Post de Facebook generado", post)
        
        # Save to file
        add_item_to_file(Files.facebook_results, post)
        
        return post