"""Instagram Generator for Social-GPT using modern OpenAI API."""
from utils import add_item_to_file
from prompts import Prompts
from brands import Brand
from files import Files
from logger import Logger
from llm import LLM, GenerationMode, GenerationItemType


class InstagramGenerator:
    def __init__(self, brand: Brand, language: str, idea: str, prompt_expansion: str, generation_mode: GenerationMode):
        self.brand = brand
        self.language = language
        self.idea = idea
        self.prompt_expansion = prompt_expansion
        self.generation_mode = generation_mode

    def generate_post(self):
        """
        Generate an Instagram post based on the given idea and brand guidelines.
        
        Returns:
            str: The generated Instagram post content
        """
        # Build the system prompt with brand description
        system_prompt = {
            "role": "system",
            "content": f"""Eres un experto en crear contenido altamente atractivo para Instagram que genera engagement y conecta con la audiencia.
Vas a crear contenido para la siguiente marca:
{self.brand.description}

IMPORTANTE: Si la idea o las instrucciones del usuario mencionan promocionar un producto o servicio específico, 
tu post DEBE enfocarse directamente en promocionar ese producto/servicio, enfatizando sus características visuales,
beneficios clave y propuesta de valor única. Incluye un llamado a la acción claro.
"""
        }
        
        # Build the user prompt with language, idea, and brand style
        prompt = f"""Escribe un post de Instagram en {self.language} que trate sobre esta idea específica:
'{self.idea}'

El post debe:
1. Tener un inicio cautivador que atrape la atención al deslizar
2. Incluir texto descriptivo que complemente una imagen visual (aunque no describes la imagen)
3. Utilizar emojis de manera estratégica para aumentar el engagement
4. Incorporar hashtags relevantes que amplíen el alcance
5. Terminar con una pregunta o llamado a la acción para fomentar la interacción{Prompts.get_avoids()}{Prompts.build_style_prompt(self.brand.style)}"""

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
        Logger.log("Post de Instagram generado", post)
        
        # Save to file
        add_item_to_file(Files.instagram_results, post)
        
        return post