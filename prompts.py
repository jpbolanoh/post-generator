from style import default_writting_style_definitions
from brands import Brand


class Prompts:

    @staticmethod
    def get_avoids():
        return "\n\nNota: evita incluir cualquier texto o ideas que requieran información actualizada, o que puedan contener datos falsos, o que mencionen un enlace real o un producto/servicio ofrecido"

    def build_style_prompt(style_items: str):
        return '\n\nSigue estas pautas de estilo:' + ', '.join(style_items)
