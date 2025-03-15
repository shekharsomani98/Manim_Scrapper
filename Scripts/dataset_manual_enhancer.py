import json
import requests
from time import sleep

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"

def ollama_prompt(code, model="llama3.2", max_retries=3):
    """Generate prompts using local Ollama model"""
    system_prompt = """You are a Manim animation expert. Analyze this Manim code and create a concise natural language prompt that describes its functionality. Follow these rules:
1. Start with action verbs like "Create", "Demonstrate", or "Show"
2. Mention key visual elements and transformations
3. Keep under 20 words
4. Avoid technical terms like 'class' or 'method'"""

    full_prompt = f"{system_prompt}\n\nManim code:\n{code}\n\nPrompt:"

    for attempt in range(max_retries):
        try:
            response = requests.post(
                OLLAMA_ENDPOINT,
                json={
                    "model": model,
                    "prompt": full_prompt,
                    "system": system_prompt,
                    "temperature": 0.3,
                    "max_tokens": 100,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()['response'].strip()
        except Exception as e:
            if attempt < max_retries - 1:
                sleep(2 ** attempt)
            else:
                print(f"Ollama failed: {str(e)}")
                return "Generate Manim animation"

def enhance_dataset(input_path, output_path):
    """Process dataset with Ollama prompt generation"""
    enhanced = []
    
    with open(input_path, 'r') as f:
        entries = [json.loads(line) for line in f]
    
    for i, entry in enumerate(entries):
        code = entry['response']
        if code.strip() != "":
            try:
                new_prompt = ollama_prompt(code)
                enhanced.append({
                    "prompt": new_prompt,
                    "response": code,
                    "original_prompt": entry.get('prompt', '')
                })
                print(f"Processed {i+1}/{len(entries)}")
                sleep(1)  # Add delay between requests
            except Exception as e:
                print(f"Error processing entry {i}: {str(e)}")
    
    with open(output_path, 'w') as f:
        for entry in enhanced:
            f.write(json.dumps(entry) + '\n')

# Usage
enhance_dataset(
    input_path='manimml_dataset.jsonl',
    output_path='manim_ollama_ml_dataset.jsonl'
)