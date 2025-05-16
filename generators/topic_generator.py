"""Topic Generator for Social-GPT using modern OpenAI API."""
from utils import format_list, write_to_file
from brands import Brand
from prompts import Prompts
from llm import LLM, GenerationMode, GenerationItemType
from logger import Logger
from files import Files


class TopicGenerator:
    def __init__(self, brand: Brand, topic_count: int, prompt_expansion: str, generation_mode: GenerationMode):
        self.brand = brand
        self.prompt_expansion = prompt_expansion
        self.topic_count = topic_count
        self.generation_mode = generation_mode

    def generate_topics(self):
        """
        Generate topics for social media posts based on brand description and user requirements.
        
        Returns:
            List of generated topics
        """
        # Build the system prompt with brand description
        system_prompt = {
            "role": "system",
            "content": f"""Eres un experto en marketing digital y contenido para redes sociales especializado en la marca siguiente:
{self.brand.description}

Tu tarea es identificar y generar temas específicos y relevantes para campañas de redes sociales basados en las instrucciones del usuario.
Si las instrucciones del usuario mencionan promocionar un producto o servicio específico, SIEMPRE asegúrate de que los temas estén directamente relacionados con ese producto o servicio.
"""
        }
        
        # Build the user prompt with topic count and any additional instructions
        prompt = f"""Genera {self.topic_count} temas específicos para posts de redes sociales en el formato:
- [Tema 1]
- [Tema 2]
- etc.

Los temas deben:
1. Ser específicos, atractivos y directamente relevantes para la marca
2. Estar orientados a la acción o beneficio cuando sea apropiado
3. Ser claros, concisos y enfocados (5-10 palabras cada uno)
4. Evitar ser demasiado genéricos{Prompts.get_avoids()}"""

        if self.prompt_expansion:
            prompt = prompt + f"\n\nInstrucciones adicionales (MUY IMPORTANTES, DEBEN SER PRIORIZADAS): {self.prompt_expansion}"
            
        user_prompt = {
            "role": "user",
            "content": prompt
        }
        
        # Generate topics using the LLM
        response = LLM.generate(
            [system_prompt, user_prompt],
            GenerationItemType.TOPICS,
            self.generation_mode
        )
        
        # Process the response to extract the topics
        topics = [
            i.replace("- ", "")
            for i in response.content.strip().split("\n")
            if len(i) > 2
        ][: self.topic_count]
        
        # Log the results
        print('\n---------')
        Logger.log("Temas generados", format_list(topics))
        
        # Save to file
        write_to_file(Files.topic_results, '\n'.join(topics))
        
        return topics