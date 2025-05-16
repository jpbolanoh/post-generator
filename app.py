import streamlit as st
import os
import pandas as pd
from PIL import Image
import io
import base64
from datetime import datetime
import openai
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importamos los componentes necesarios de social-GPT
from generators.topic_generator import TopicGenerator
from generators.idea_generator import IdeaGenerator
from generators.tweet_generator import TweetGenerator
from generators.facebook_generator import FacebookGenerator
from generators.instagram_generator import InstagramGenerator
from generators.linkedin_generator import LinkedInGenerator
from generators.image_prompt_generator import ImagePromptGenerator
from generators.image_generator import generate_image_with_openai
from utils import prepare_directories, export_content_to_csv, export_content_to_json, export_content_to_txt
from brands import Brand
from llm import GenerationMode

# Configuración de la página
st.set_page_config(page_title="Social-GPT", page_icon="🚀", layout="wide")
prepare_directories()

def display_image(image_path):
    """Muestra una imagen desde una ruta de archivo en Streamlit."""
    try:
        image = Image.open(image_path)
        st.image(image, use_container_width=True)
        return True
    except Exception as e:
        st.error(f"Error al mostrar la imagen: {e}")
        return False

def main():
    # Añadimos título y descripción
    st.title("Social-GPT 🚀")
    st.subheader("Generador de Contenido para Redes Sociales Impulsado por IA")
    
    # Obtener la API key desde el archivo .env
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    
    # Test OpenAI API Key
    if not openai_api_key:
        st.error("No se encontró la clave API de OpenAI. Asegúrate de tener un archivo .env con OPENAI_API_KEY configurada.")
        st.stop()
    
    # Set the API key for OpenAI
    try:
        # Test the API key
        client = openai.OpenAI(api_key=openai_api_key)
        models = client.models.list()
        st.success("✅ Conexión a OpenAI establecida correctamente")
    except Exception as e:
        st.error(f"❌ Error con la clave API: {e}")
        st.stop()
    
    # Tabs para diferentes funciones
    tab1, tab2, tab3 = st.tabs(["Configurar Marca", "Generar Contenido", "Contenido Generado"])
    
    with tab1:
        st.header("Configuración de Marca")
        
        # Sección de selección de marca
        st.subheader("Seleccionar o Crear una Marca")
        
        cached_brands = Brand.get_cached_brands()
        brand_names = [brand.title for brand in cached_brands]
        brand_names.append("Crear nueva marca")
        
        selected_brand_name = st.selectbox(
            "Selecciona una marca o crea una nueva",
            options=brand_names
        )
        
        if selected_brand_name == "Crear nueva marca":
            st.subheader("Crear Nueva Marca")
            new_brand_name = st.text_input("Nombre de la Marca")
            new_brand_description = st.text_area("Descripción de la Marca", height=150)
            
            style_options = ["Profesional", "Casual", "Informativo", "Inspirador", 
                            "Humorístico", "Educativo", "Promocional", "Narrativo", 
                            "Basado en preguntas", "Llamado a la acción", "Atractivo", "Auténtico"]
            selected_styles = st.multiselect("Selecciona definiciones de estilo", options=style_options, 
                                           default=["Profesional", "Informativo"])
            
            if st.button("Crear Marca"):
                if new_brand_name and new_brand_description and selected_styles:
                    brand = Brand(new_brand_name, new_brand_description, selected_styles)
                    brand.save_in_cache()
                    st.success(f"¡Marca '{new_brand_name}' creada exitosamente!")
                    st.session_state.brand = brand
                else:
                    st.error("Por favor completa toda la información de la marca.")
        else:
            # Mostrar la información de la marca seleccionada
            selected_brand = None
            for brand in cached_brands:
                if brand.title == selected_brand_name:
                    selected_brand = brand
                    break
            
            if selected_brand:
                st.subheader(f"Marca: {selected_brand.title}")
                st.markdown(f"**Descripción:**\n{selected_brand.description}")
                st.markdown(f"**Estilos:**\n{', '.join(selected_brand.style)}")
                
                if st.button("Usar Esta Marca"):
                    st.session_state.brand = selected_brand
                    st.success(f"¡Marca '{selected_brand.title}' seleccionada!")
    
    with tab2:
        st.header("Generar Contenido")
        
        # Verificar si hay una marca seleccionada
        if 'brand' not in st.session_state:
            st.warning("Por favor selecciona o crea una marca en la pestaña 'Configurar Marca'.")
            st.stop()
        
        st.subheader(f"Generando contenido para: {st.session_state.brand.title}")
        
        # Configuración de generación de contenido
        col1, col2 = st.columns(2)
        
        with col1:
            topic_count = st.number_input("Número de temas a generar", min_value=1, max_value=20, value=3)
            ideas_per_topic = st.number_input("Número de posts por tema", min_value=1, max_value=10, value=2)
            posts_language = st.text_input("Idioma de los posts", value="Español")
        
        with col2:
            topics_ideas_prompt_expansion = st.text_area("Instrucciones específicas (MUY IMPORTANTE)", 
                placeholder="Por ejemplo: 'Quiero promocionar nuestra nueva app de productividad llamada WorkFlow Pro que ayuda a organizar tareas y aumentar la eficiencia'",
                height=100)
            posts_prompt_expansion = st.text_area("Estilo o enfoque específico para los posts", 
                placeholder="Por ejemplo: 'Enfatizar los beneficios de ahorro de tiempo' o 'Enfocarse en la facilidad de uso'",
                height=100)
        
        # Selección de plataformas
        platform_options = ["Instagram", "Facebook", "Twitter", "LinkedIn"]
        selected_platforms = st.multiselect("¿Qué plataformas quieres utilizar?", 
                                          options=platform_options,
                                          default=["Twitter", "Instagram"])
        
        # Opción de generación de imágenes
        generate_images = st.checkbox("Generar imágenes para el contenido (usando DALL-E 3 de OpenAI)", value=True)
        
        # Configuración avanzada para imágenes
        with st.expander("Configuración avanzada", expanded=False):
            st.subheader("Configuración de generación de imágenes")
            
            # Tamaño de imagen
            image_size = st.radio(
                "Tamaño de imagen",
                ["1024x1024 (cuadrado)", "1792x1024 (horizontal)", "1024x1792 (vertical)"],
                index=0
            )
            
            # Calidad de imagen
            image_quality = st.radio(
                "Calidad de imagen",
                ["Estándar", "HD"],
                index=0,
                help="HD produce imágenes más detalladas pero consume más créditos."
            )
            
            # Guardar en session state
            st.session_state.image_settings = {
                "model": "dall-e-3",
                "size": image_size.split(" ")[0],  # Extraer solo las dimensiones
                "quality": "standard" if image_quality == "Estándar" else "hd"
            }
        
        # Selección de calidad de generación
        quality_options = ["Calidad baja (rápido + económico)", "Calidad media (recomendado)", "Calidad alta (lento + costoso)"]
        selected_quality = st.selectbox("Calidad de generación", options=quality_options, index=1)
        
        # Mapeamos las opciones en español a los valores en inglés que espera la aplicación
        quality_mapping = {
            "Calidad baja (rápido + económico)": "Low quality (fast + cheap)",
            "Calidad media (recomendado)": "Medium quality (recommended)",
            "Calidad alta (lento + costoso)": "High quality (slow + expensive)"
        }
        
        generation_mode = GenerationMode.from_string(quality_mapping[selected_quality])
        
        # Botón de generación
        if st.button("Generar Contenido"):
            if not selected_platforms:
                st.error("Por favor, selecciona al menos una plataforma.")
                st.stop()
            
            if not openai_api_key:
                st.error("No se encuentra la clave API de OpenAI.")
                st.stop()
            
            with st.spinner("Generando contenido..."):
                # Guardamos la instancia de marca
                brand = st.session_state.brand
                
                # Creamos una barra de progreso
                progress = st.progress(0)
                status_text = st.empty()
                
                # Generamos temas
                status_text.text("Generando temas...")
                
                # Preprocesar instrucciones del usuario para identificar peticiones de promoción
                is_promotional = any(keyword in topics_ideas_prompt_expansion.lower() for keyword in 
                                   ["promocion", "promoción", "venta", "producto", "servicio", "app", "aplicación", "lanzamiento", "nueva"])
                
                if is_promotional:
                    # Si detectamos que es una petición promocional, aseguramos que los temas se centran en eso
                    enhanced_prompt = f"IMPORTANTE: Este contenido debe promocionar o vender un producto/servicio. {topics_ideas_prompt_expansion}"
                else:
                    enhanced_prompt = topics_ideas_prompt_expansion
                
                # Generar temas con el prompt mejorado
                topics = TopicGenerator(
                    brand, topic_count, enhanced_prompt, generation_mode
                ).generate_topics()
                
                # Calculamos total de elementos a generar para seguimiento del progreso
                # 1 para cada generación de idea + número de plataformas por idea + 1 para generación de imagen si está habilitada
                items_per_idea = len(selected_platforms) + (1 if generate_images else 0)
                # Total = (generación de temas) + (ideas por tema) + (plataformas + imágenes por idea)
                total_items = 1 + (len(topics) * ideas_per_topic * (1 + items_per_idea))
                items_completed = 1  # Comenzamos en 1 para contabilizar los temas ya generados
                
                # Información de depuración (oculta en una sección colapsada)
                with st.expander("Información de depuración", expanded=False):
                    st.write(f"Total de elementos a procesar: {total_items}")
                    st.write(f"Elementos completados: {items_completed}")
                    st.write(f"Valor de progreso: {items_completed/total_items:.4f}")
                    st.write(f"Número de temas: {len(topics)}")
                    st.write(f"Ideas por tema: {ideas_per_topic}")
                    st.write(f"Plataformas seleccionadas: {len(selected_platforms)}")
                    st.write(f"Generar imágenes: {generate_images}")
                
                # Almacenamos contenido generado para mostrar
                st.session_state.generated_content = {
                    "topics": topics,
                    "ideas": [],
                    "posts": {},
                    "images": []
                }
                
                for platform in selected_platforms:
                    st.session_state.generated_content["posts"][platform] = []
                
                # Procesamos cada tema
                for topic in topics:
                    status_text.text(f"Generando ideas para el tema: {topic}")
                    
                    # Generamos ideas para este tema
                    if is_promotional:
                        # Si es promocional, aseguramos que las ideas también lo sean
                        enhanced_idea_prompt = f"IMPORTANTE: Estas ideas deben promocionar directamente el producto/servicio mencionado: {topics_ideas_prompt_expansion}"
                    else:
                        enhanced_idea_prompt = topics_ideas_prompt_expansion
                        
                    ideas = IdeaGenerator(
                        brand, ideas_per_topic, enhanced_idea_prompt, generation_mode
                    ).generate_ideas(topic)
                    
                    st.session_state.generated_content["ideas"].extend([(topic, idea) for idea in ideas])
                    items_completed += 1
                    progress_value = min(items_completed / total_items, 1.0)
                    # Actualizar info de depuración
                    st.expander("Información de depuración").write(f"Después de ideas para tema '{topic}': {items_completed}/{total_items} = {progress_value:.4f}")
                    # Actualizar barra de progreso
                    progress.progress(progress_value)
                    
                    # Generamos contenido para cada idea
                    for idea in ideas:
                        for platform in selected_platforms:
                            status_text.text(f"Generando contenido de {platform} para idea: {idea}")
                            
                            # Prepara instrucciones específicas para el post
                            if is_promotional:
                                enhanced_post_prompt = f"IMPORTANTE - PROMOCIÓN: {topics_ideas_prompt_expansion}\nEstilo específico: {posts_prompt_expansion}"
                            else:
                                enhanced_post_prompt = posts_prompt_expansion
                                
                            if platform == "Twitter":
                                post = TweetGenerator(
                                    brand, posts_language, idea, enhanced_post_prompt, generation_mode
                                ).generate_tweet()
                                st.session_state.generated_content["posts"]["Twitter"].append((topic, idea, post))
                            
                            elif platform == "Facebook":
                                post = FacebookGenerator(
                                    brand, posts_language, idea, enhanced_post_prompt, generation_mode
                                ).generate_post()
                                st.session_state.generated_content["posts"]["Facebook"].append((topic, idea, post))
                            
                            elif platform == "Instagram":
                                post = InstagramGenerator(
                                    brand, posts_language, idea, enhanced_post_prompt, generation_mode
                                ).generate_post()
                                st.session_state.generated_content["posts"]["Instagram"].append((topic, idea, post))
                            
                            elif platform == "LinkedIn":
                                post = LinkedInGenerator(
                                    brand, posts_language, idea, enhanced_post_prompt, generation_mode
                                ).generate_post()
                                st.session_state.generated_content["posts"]["LinkedIn"].append((topic, idea, post))
                            
                            items_completed += 1
                            progress_value = min(items_completed / total_items, 1.0)
                            # Actualizar info de depuración
                            st.expander("Información de depuración").write(f"Después de post de {platform} para '{idea}': {items_completed}/{total_items} = {progress_value:.4f}")
                            # Actualizar barra de progreso
                            progress.progress(progress_value)
                        
                        # Generar imagen si está seleccionado
                        if generate_images:
                            status_text.text(f"Generando imagen para idea: {idea}")
                            try:
                                # Obtener configuración de imágenes del session state
                                image_settings = st.session_state.get('image_settings', {
                                    "model": "dall-e-3",
                                    "size": "1024x1024",
                                    "quality": "standard"
                                })
                                
                                # Pasar las instrucciones promocionales al generador de prompts de imágenes
                                if is_promotional:
                                    image_instructions = f"PROMOCIONAL: {topics_ideas_prompt_expansion}"
                                else:
                                    image_instructions = None
                                    
                                image_prompt = ImagePromptGenerator(
                                    brand, idea, generation_mode, image_instructions
                                ).generate_prompt()
                                
                                image_path = generate_image_with_openai(
                                    image_prompt, 
                                    generation_mode,
                                    model_preference="dall-e-3",
                                    size=image_settings["size"],
                                    quality=image_settings["quality"]
                                )
                                st.session_state.generated_content["images"].append((topic, idea, image_path))
                            except Exception as e:
                                st.error(f"Error al generar imagen: {e}")
                        
                            items_completed += 1
                            progress_value = min(items_completed / total_items, 1.0)
                            # Actualizar info de depuración
                            st.expander("Información de depuración").write(f"Después de imagen para '{idea}': {items_completed}/{total_items} = {progress_value:.4f}")
                            # Actualizar barra de progreso
                            progress.progress(progress_value)
                
                # Completado
                st.expander("Información de depuración").write(f"Completado: {total_items}/{total_items} = 1.0")
                progress.progress(1.0)  # Establecer exactamente a 1.0 al final
                status_text.text("¡Generación de contenido completada!")
                st.success("¡El contenido ha sido generado exitosamente! Ve a la pestaña 'Contenido Generado' para verlo.")
    
    with tab3:
        st.header("Contenido Generado")
        
        if 'generated_content' not in st.session_state:
            st.info("Aún no se ha generado contenido. Por favor, ve a la pestaña 'Generar Contenido' para crear contenido.")
            st.stop()
        
        # Creamos pestañas para cada tipo de contenido
        topic_tab, idea_tab, post_tab, image_tab, export_tab = st.tabs(["Temas", "Ideas", "Posts", "Imágenes", "Exportar"])
        
        with topic_tab:
            st.subheader("Temas Generados")
            for i, topic in enumerate(st.session_state.generated_content["topics"]):
                st.markdown(f"**{i+1}. {topic}**")
        
        with idea_tab:
            st.subheader("Ideas Generadas")
            # Agrupamos ideas por tema
            ideas_by_topic = {}
            for topic, idea in st.session_state.generated_content["ideas"]:
                if topic not in ideas_by_topic:
                    ideas_by_topic[topic] = []
                ideas_by_topic[topic].append(idea)
            
            for topic, ideas in ideas_by_topic.items():
                st.markdown(f"### Tema: {topic}")
                for i, idea in enumerate(ideas):
                    st.markdown(f"**{i+1}. {idea}**")
                st.markdown("---")
        
        with post_tab:
            st.subheader("Posts Generados")
            
            # Selección de plataforma para visualización
            platforms = list(st.session_state.generated_content["posts"].keys())
            if not platforms:
                st.info("No se han generado posts.")
                st.stop()
            
            selected_view_platform = st.selectbox("Selecciona plataforma para ver", options=platforms)
            
            posts = st.session_state.generated_content["posts"][selected_view_platform]
            
            if not posts:
                st.info(f"No se han generado posts para {selected_view_platform}.")
                st.stop()
            
            # Mostrar posts
            for topic, idea, post in posts:
                with st.expander(f"Tema: {topic} | Idea: {idea}"):
                    st.markdown(post)
                    st.markdown("---")
                    # Añadir botón de copiar
                    if st.button(f"Copiar al portapapeles", key=f"copy_{selected_view_platform}_{post[:20]}"):
                        st.write("¡Copiado al portapapeles!")
                        st.session_state["clipboard"] = post
        
        with image_tab:
            st.subheader("Imágenes Generadas")
            
            if not st.session_state.generated_content["images"]:
                st.info("No se han generado imágenes.")
                st.stop()
            
            # Mostrar imágenes en una cuadrícula (3 columnas)
            cols = st.columns(3)
            for i, (topic, idea, image_path) in enumerate(st.session_state.generated_content["images"]):
                with cols[i % 3]:
                    st.markdown(f"**Tema:** {topic}")
                    st.markdown(f"**Idea:** {idea}")
                    display_image(image_path)
                    st.markdown("---")
        
        with export_tab:
            st.subheader("Exportar Contenido Generado")
            
            # Opciones de exportación
            export_format = st.selectbox("Formato de exportación", options=["CSV", "JSON", "TXT"])
            
            if st.button("Exportar Contenido"):
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    if export_format == "CSV":
                        filename = f"contenido_social_{timestamp}.csv"
                        output_path = export_content_to_csv(st.session_state.generated_content, filename)
                        
                    elif export_format == "JSON":
                        filename = f"contenido_social_{timestamp}.json"
                        output_path = export_content_to_json(st.session_state.generated_content, filename)
                        
                    elif export_format == "TXT":
                        filename = f"contenido_social_{timestamp}.txt"
                        output_path = export_content_to_txt(st.session_state.generated_content, filename)
                    
                    # Leer el archivo para descarga
                    with open(output_path, "rb") as file:
                        file_contents = file.read()
                    
                    # Crear botón de descarga
                    st.download_button(
                        label=f"Descargar archivo {export_format}",
                        data=file_contents,
                        file_name=filename,
                        mime="application/octet-stream"
                    )
                    
                    st.success(f"¡Contenido exportado exitosamente a {filename}!")
                    
                except Exception as e:
                    st.error(f"Error durante la exportación: {e}")

if __name__ == "__main__":
    main()