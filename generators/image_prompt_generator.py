"""Generador de Prompts de Imágenes para Social-GPT optimizado para DALL-E 3."""
from brands import Brand
from llm import LLM, GenerationMode, GenerationItemType

class ImagePromptGenerator:
    def __init__(self, brand: Brand, post_idea: str, generation_mode: GenerationMode, additional_instructions=None):
        self.brand = brand
        self.post_idea = post_idea
        self.generation_mode = generation_mode
        self.additional_instructions = additional_instructions

    def generate_prompt(self):
        """
        Genera un prompt optimizado para DALL-E 3 basado en la idea del post.
        
        Returns:
            str: Un prompt bien elaborado para la generación de imágenes con DALL-E 3
        """
        # Prompt de sistema para el modelo
        system_content = f"""Eres un experto en crear prompts detallados y creativos para el modelo DALL-E 3 de OpenAI. 
Estás ayudando a crear imágenes para redes sociales para una marca con esta descripción: 
{self.brand.description}"""

        # Si hay instrucciones promocionales, añadirlas al prompt del sistema
        if self.additional_instructions and "PROMOCIONAL" in self.additional_instructions:
            system_content += f"""

IMPORTANTE: Esta imagen debe tener un enfoque PROMOCIONAL para un producto o servicio. 
Asegúrate de que el prompt genere una imagen que comunique visualmente el valor y atractivo del producto/servicio.
La imagen debe ser profesional, atractiva y orientada a marketing."""

        system_prompt = {
            "role": "system", 
            "content": system_content
        }

        # Prompt del usuario solicitando la descripción de la imagen
        user_content = f"""Crea un prompt atractivo y detallado para una imagen de redes sociales sobre:
'{self.post_idea}'

El prompt debe:
1. Ser visualmente descriptivo y atractivo (25-50 palabras)
2. Relacionarse claramente con la idea del post y la identidad de la marca
3. Evitar solicitar texto en la imagen (DALL-E tiene dificultades con el texto)
4. Centrarse en escenas, objetos y entornos que representen la idea metafóricamente
5. Incluir dirección artística como iluminación, estilo, ambiente y perspectiva
6. Evitar mencionar "publicación de redes sociales" en la descripción
7. Nunca solicitar contenido prohibido (personas reales, violencia, temas políticos)

Devuelve SOLO el texto del prompt de la imagen sin explicaciones ni formato adicional."""

        # Si hay instrucciones adicionales, añadirlas al prompt del usuario
        if self.additional_instructions:
            user_content += f"\n\nInstrucciones adicionales: {self.additional_instructions}"
        
        user_prompt = {
            "role": "user",
            "content": user_content
        }

        # Obtener la descripción base usando el LLM
        base_description = LLM.generate(
            [system_prompt, user_prompt], 
            GenerationItemType.IMAGE_PROMPT, 
            self.generation_mode
        ).content.strip()
        
        # Añadir detalles técnicos para crear el prompt final
        brand_style = ", ".join(self.brand.style)
        
        # Si es promocional, añadir estilos específicos para marketing
        if self.additional_instructions and "PROMOCIONAL" in self.additional_instructions:
            final_prompt = f"""{base_description}

Estilo: Profesional, calidad comercial de marketing premium, {brand_style}, ideal para publicidad de productos.
Detalles técnicos: 4K, altamente detallado, iluminación de estudio profesional, composición llamativa, enfoque nítido, colores vibrantes y atractivos."""
        else:
            final_prompt = f"""{base_description}

Estilo: Profesional, calidad comercial, {brand_style}, adecuado para una publicación de marca en redes sociales.
Detalles técnicos: 4K, altamente detallado, iluminación profesional, profundidad de campo, enfoque nítido."""

        return final_prompt