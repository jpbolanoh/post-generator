from utils import add_item_to_file, ask_boolean
from style import writting_style_definitions, default_writting_style_definitions
from files import Files


class Brand:

    def __init__(self, title, description, style):
        self.title = title
        self.description = description
        self.style = style

    @staticmethod
    def split_file_text(text):
        title = text.split(" - ")[0].split('. ')[1] if '. ' in text.split(" - ")[0] else text.split(" - ")[0]
        content = text.split(" - ")[1]
        return [title, content]

    def to_description_cache_text(self):
        return f"{self.title} - {self.description}"

    def to_style_cache_text(self):
        return f"{self.title} - {', '.join(self.style)}"

    @staticmethod
    def from_title(title: str):
        brands = Brand.get_cached_brands()
        for brand in brands:
            if brand.title == title:
                return brand

    @staticmethod
    def create_new_brand(title="", description="", styles=None):
        """
        Versión simplificada para uso en Streamlit sin inquirer.
        Los parámetros se pasan directamente en lugar de preguntar.
        """
        if styles is None:
            styles = default_writting_style_definitions
        
        brand = Brand(title, description, styles)
        add_item_to_file(Files.brand_descriptions,
                         brand.to_description_cache_text())
        add_item_to_file(Files.brand_styles, brand.to_style_cache_text())
        return brand

    @staticmethod
    def parse_brand_file(file: str):
        with open(file, 'r') as f:
            brand_texts = []
            last_line = ""
            for line in f:
                if line.strip() == "---":
                    brand_texts.append(last_line)
                    last_line = ""
                else:
                    last_line += line.strip()
        mapped_brands = {}
        for brand_text in brand_texts:
            if " - " in brand_text:
                [title, content] = Brand.split_file_text(brand_text)
                mapped_brands[title] = content
        return mapped_brands

    @staticmethod
    def request_brand():
        """
        Versión simplificada para Streamlit que retorna el primer brand disponible
        o crea uno nuevo si no hay ninguno.
        
        En la versión Streamlit, la selección de marca se hace mediante la UI.
        """
        cached_brands = Brand.get_cached_brands()
        if not cached_brands:
            return Brand.create_new_brand(
                "Marca de ejemplo", 
                "Esta es una marca de ejemplo creada automáticamente.", 
                default_writting_style_definitions
            )
        return cached_brands[0]  # Retorna el primer brand disponible

    @staticmethod
    def get_cached_brands():
        """Obtiene las marcas desde los archivos de caché."""
        descriptions_map = {}
        styles_map = {}
        
        try:
            descriptions_map = Brand.parse_brand_file(Files.brand_descriptions)
            styles_map = Brand.parse_brand_file(Files.brand_styles)
        except Exception as e:
            print(f"Error al cargar marcas: {e}")
            return []

        brands = []
        for brand in descriptions_map:
            if brand in styles_map:
                brand_obj = Brand(
                    brand, descriptions_map[brand], styles_map[brand].split(', '))
                brands.append(brand_obj)
        return brands

    def save_in_cache(self):
        add_item_to_file(Files.brand_descriptions,
                         self.to_description_cache_text())
        add_item_to_file(Files.brand_styles, self.to_style_cache_text())