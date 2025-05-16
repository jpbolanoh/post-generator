"""Idea Generator for Social-GPT using modern OpenAI API."""
from utils import format_list, add_item_to_file
from prompts import Prompts
from files import Files
from brands import Brand
from logger import Logger
from llm import LLM, GenerationMode, GenerationItemType


class IdeaGenerator:
    def __init__(self, brand: Brand, number_of_ideas: int, prompt_expansion: str, generation_mode: GenerationMode):
        self.brand = brand
        self.number_of_ideas = number_of_ideas
        self.prompt_expansion = prompt_expansion
        self.generation_mode = generation_mode

    def generate_ideas(self, topic):
        """
        Generate specific post ideas for a given topic based on brand guidelines.
        
        Args:
            topic: The general topic to generate ideas for
            
        Returns:
            List of generated ideas
        """
        # Build the system prompt with brand description
        system_prompt = {
            "role": "system",
            "content": f"""Eres un experto creativo en marketing digital y contenido para redes sociales especializado en la marca siguiente:
{self.brand.description}

Tu trabajo es crear ideas específicas y atractivas para posts de redes sociales basadas en un tema dado.
Si las instrucciones del usuario mencionan promocionar un producto o servicio específico, SIEMPRE asegúrate de que las ideas de post promocionen directamente ese producto o servicio, enfatizando sus beneficios, características o valor único.
"""
        }
        
        # Build the user prompt with topic and additional instructions
        base_prompt = f"""Genera {self.number_of_ideas} ideas creativas y específicas para posts de redes sociales sobre el tema '{topic}' en formato de lista:
- [Idea 1]
- [Idea 2]
- etc.

Cada idea debe:
1. Ser una propuesta concreta de contenido para un único post
2. Incluir un enfoque o ángulo específico (no solo el tema general)
3. Ser atractiva, original y adaptada a la marca
4. Estar lista para desarrollarse en un post completo{Prompts.get_avoids()}{Prompts.build_style_prompt(self.brand.style)}"""
        
        if self.prompt_expansion:
            base_prompt += f"\n\nInstrucciones adicionales (MUY IMPORTANTES, DEBEN SER PRIORIZADAS): {self.prompt_expansion}"
            
        user_prompt = {
            "role": "user",
            "content": base_prompt
        }
        
        # Generate ideas using the LLM
        response = LLM.generate(
            [system_prompt, user_prompt],
            GenerationItemType.IDEAS,
            self.generation_mode
        )
        
        # Process the response to extract the ideas
        ideas = [
            i.replace("- ", "")
            for i in response.content.strip().split("\n")
            if len(i) > 2
        ][: self.number_of_ideas]
        
        # Log the results
        Logger.log("Ideas generadas", format_list(ideas))
        
        # Save to file
        for idea in ideas:
            add_item_to_file(Files.idea_results, idea)
        
        return ideas