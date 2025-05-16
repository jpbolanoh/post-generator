"""
Main script for Social-GPT console application.
Use app.py for the Streamlit UI version.
"""
import os
import inquirer
from utils import ask_boolean, prepare_directories
from generators.topic_generator import TopicGenerator
from generators.idea_generator import IdeaGenerator
from generators.tweet_generator import TweetGenerator
from generators.facebook_generator import FacebookGenerator
from generators.instagram_generator import InstagramGenerator
from generators.linkedin_generator import LinkedInGenerator
from generators.image_prompt_generator import ImagePromptGenerator
from generators.image_generator import generate_image_with_openai
from brands import Brand
from llm import LLM, GenerationMode


def main():
    """Main function for Social-GPT console application."""
    prepare_directories()

    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        api_key = input("\nPlease enter your OpenAI API key (it will be stored temporarily):\n")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        else:
            print("No API key provided. Exiting.")
            return

    # Get brand information
    brand = Brand.request_brand()
    
    # Get generation parameters
    topic_count = int(input("\nNumber of topics to generate?\n"))
    ideas_per_topic = int(input("\nNumber of posts per topic?\n"))
    posts_language = input("\nLanguage of the posts?\n")
    topics_ideas_prompt_expansion = input(
        "\nAny specific request about the TOPICS/IDEAS?\n") or ""
    posts_prompt_expansion = input(
        "\nAny specific request about the style or content of the POSTS?\n") or ""
    generate_images = ask_boolean(
        "\nUse image generation feature (GPT-image-1)?", False)
    
    # Select platforms
    print("\n")
    platforms = inquirer.prompt([inquirer.Checkbox('platforms', message="Which platforms do you want to target?", choices=[
        "Instagram", "Facebook", "Twitter", "LinkedIn"])])['platforms']

    # Select generation mode
    mode = LLM.request_generation_mode()

    print('\n👍🏼 Nice! Started generating...\n')

    # Generate topics
    topics = TopicGenerator(
        brand, topic_count, topics_ideas_prompt_expansion, mode).generate_topics()

    # Process each topic
    for topic in topics:
        # Generate ideas for this topic
        ideas = IdeaGenerator(
            brand, ideas_per_topic, topics_ideas_prompt_expansion, mode).generate_ideas(topic)

        # Process each idea
        for idea in ideas:
            # Generate platform-specific content
            if "Twitter" in platforms:
                TweetGenerator(brand, posts_language, idea,
                              posts_prompt_expansion, mode).generate_tweet()
            if "Facebook" in platforms:
                FacebookGenerator(brand, posts_language, idea,
                                posts_prompt_expansion, mode).generate_post()
            if "Instagram" in platforms:
                InstagramGenerator(brand, posts_language, idea,
                                 posts_prompt_expansion, mode).generate_post()
            if "LinkedIn" in platforms:
                LinkedInGenerator(brand, posts_language, idea,
                                posts_prompt_expansion, mode).generate_post()
            
            # Generate images if requested
            if generate_images:
                if not api_key:
                    print(
                        "🚨 You need to set the OPENAI_API_KEY environment variable to use the image generation feature")
                else:
                    try:
                        image_prompt = ImagePromptGenerator(
                            brand, idea, mode).generate_prompt()
                        generate_image_with_openai(image_prompt, mode)
                    except Exception as e:
                        print(f"Error generating image: {e}")

    print('\n\n✅ Done!')


if __name__ == "__main__":
    main()