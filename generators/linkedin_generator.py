"""LinkedIn Generator for Social-GPT using modern OpenAI API."""
from utils import add_item_to_file
from prompts import Prompts
from brands import Brand
from files import Files
from logger import Logger
from llm import LLM, GenerationMode, GenerationItemType


class LinkedInGenerator:
    def __init__(self, brand: Brand, language: str, idea: str, prompt_expansion: str, generation_mode: GenerationMode):
        self.brand = brand
        self.language = language
        self.idea = idea
        self.prompt_expansion = prompt_expansion
        self.generation_mode = generation_mode

    def generate_post(self):
        """
        Generate a LinkedIn post based on the given idea and brand guidelines.
        
        Returns:
            str: The generated LinkedIn post content
        """
        # Build the system prompt with brand description
        system_prompt = {
            "role": "system",
            "content": f"""Eres un experto en crear contenido profesional y persuasivo para LinkedIn que genera credibilidad y posicionamiento de marca.
Vas a crear contenido para la siguiente marca:
{self.brand.description}

IMPORTANTE: Si la idea o las instrucciones del usuario mencionan promocionar un producto o servicio específico, 
tu post DEBE enfocarse directamente en promocionar ese producto/servicio desde un ángulo profesional y centrado en el valor.
Destaca cómo resuelve problemas empresariales concretos y aporta beneficios medibles.
"""
        }
        
        # Build the user prompt with language, idea, and brand style
        prompt = f"""Escribe un post de LinkedIn en {self.language} con 5-8 párrafos que trate sobre esta idea específica:
'{self.idea}'

El post debe:
1. Comenzar con un párrafo inicial potente que capte la atención profesional
2. Desarrollar el contenido con información valiosa y perspectivas relevantes
3. Incluir datos o ejemplos que refuercen el mensaje principal cuando sea posible
4. Mantener un tono profesional y experto apropiado para LinkedIn
5. Finalizar con un llamado a la acción claro para generar interacción{Prompts.get_avoids()}{Prompts.build_style_prompt(self.brand.style)}"""

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
        Logger.log("Post de LinkedIn generado", post)
        
        # Save to file
        add_item_to_file(Files.linkedin_results, post)
        
        return post