import os
import time
from datetime import datetime
import pandas as pd
import json
import threading
import tempfile

def format_list(list_items):
    """Format a list for pretty printing."""
    return "\n".join([f"- {item}" for item in list_items])

def write_to_file(file_path, content):
    """
    Write content to a file, creating directories if needed.
    Appends "---" as a separator between entries.
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Create file if it doesn't exist
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            pass
    
    # Append content with separator
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f"{content}\n---\n")

def add_item_to_file(file_path, content):
    """
    Add an item to a file, with appropriate separators.
    Used primarily for brand information caching.
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Create file if it doesn't exist
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            pass
    
    # Append content with separator
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f"{content}\n---\n")

def prepare_directories():
    """Create necessary directories for the application."""
    directories = [
        "results",
        "results/images",
        "cache"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def ask_boolean(question, default=False):
    """
    Ask a yes/no question via command line.
    
    Note: Esta versión simplificada no usa inquirer ya que no es necesario en Streamlit.
    La funcionalidad completa solo está disponible en la versión CLI.
    """
    return default  # En Streamlit siempre usamos los controles de la UI

def count_files_in_directory(directory_path):
    """Count the number of files in a directory."""
    if not os.path.exists(directory_path):
        return 0
    return len([f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))])

def retry_n_times(n, fn):
    """
    Retry a function n times before giving up.
    Returns the result of the function, or None if all attempts fail.
    """
    for i in range(n):
        try:
            return fn()
        except Exception as e:
            print(f"Attempt {i+1} failed: {e}")
            if i < n - 1:  # if not the last attempt
                print(f"Retrying in 2 seconds...")
                time.sleep(2)
    return None

def create_directory(directory):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def export_content_to_csv(content, filename="social_content.csv"):
    """Export content to CSV format."""
    # Create DataFrame from content
    data = []
    
    # Add topics
    for topic in content.get("topics", []):
        data.append({"Type": "Topic", "Topic": topic, "Idea": "", "Platform": "", "Content": ""})
    
    # Add ideas
    for topic, idea in content.get("ideas", []):
        data.append({"Type": "Idea", "Topic": topic, "Idea": idea, "Platform": "", "Content": ""})
    
    # Add posts
    for platform, posts in content.get("posts", {}).items():
        for topic, idea, post in posts:
            data.append({"Type": "Post", "Topic": topic, "Idea": idea, "Platform": platform, "Content": post})
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    df.to_csv(filename, index=False)
    return filename

def export_content_to_json(content, filename="social_content.json"):
    """Export content to JSON format."""
    with open(filename, 'w') as f:
        json.dump(content, f, indent=4)
    return filename

def export_content_to_txt(content, filename="social_content.txt"):
    """Export content to TXT format."""
    with open(filename, 'w') as f:
        # Write topics
        f.write("=== TOPICS ===\n\n")
        for i, topic in enumerate(content.get("topics", [])):
            f.write(f"{i+1}. {topic}\n")
        f.write("\n\n")
        
        # Write ideas
        f.write("=== IDEAS ===\n\n")
        ideas_by_topic = {}
        for topic, idea in content.get("ideas", []):
            if topic not in ideas_by_topic:
                ideas_by_topic[topic] = []
            ideas_by_topic[topic].append(idea)
        
        for topic, ideas in ideas_by_topic.items():
            f.write(f"Topic: {topic}\n")
            for i, idea in enumerate(ideas):
                f.write(f"  {i+1}. {idea}\n")
            f.write("\n")
        
        # Write posts by platform
        f.write("=== POSTS ===\n\n")
        for platform, posts in content.get("posts", {}).items():
            f.write(f"--- {platform} ---\n\n")
            for topic, idea, post in posts:
                f.write(f"Topic: {topic}\n")
                f.write(f"Idea: {idea}\n")
                f.write(f"Post:\n{post}\n\n")
                f.write("-" * 50 + "\n\n")
    
    return filename

def ensure_file_created(filename: str):
    """Create an empty file if it doesn't exist yet."""
    if not os.path.exists(filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            pass