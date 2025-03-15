import json
import requests
from time import sleep
from pathlib import Path

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"  # Can use "llama2" or "codellama" as well

def generate_prompt_with_ollama(code):
    """Generate natural language prompt using Ollama"""
    system_prompt = """You are a Manim animation expert. Analyze this Manim code and create a concise natural language prompt that describes its functionality. Follow these rules:
1. Start with action verbs like "Create", "Demonstrate", or "Show"
2. Mention key visual elements and transformations
3. Keep under 20 words
4. Avoid technical terms like 'class' or 'method'"""

    try:
        response = requests.post(
            OLLAMA_ENDPOINT,
            json={
                "model": MODEL_NAME,
                "prompt": f"Manim code:\n{code}\n\nPrompt:",
                "system": system_prompt,
                "temperature": 0.3,
                "max_tokens": 100,
                "stream": False
            }
        )
        return response.json()['response'].strip()
    except Exception as e:
        print(f"Error generating prompt: {str(e)}")
        return None

def process_entry(entry):
    """Process a single JSON entry to create prompt-response pair"""
    if 'examples' not in entry or not entry['examples']:
        return None
    
    code = entry['examples'][0]['code']
    print(code)
    generated_prompt = generate_prompt_with_ollama(code)
    
    if not generated_prompt:
        return None
    
    return {
        "prompt": generated_prompt,
        "response": code,
        "metadata": {
            "source": entry.get('source_link', ''),
            "original_name": entry.get('name', '')
        }
    }

def create_prompt_dataset(input_path, output_path):
    """Main function to process dataset"""
    input_file = Path(input_path)
    output_file = Path(output_path)
    
    with input_file.open('r') as infile, output_file.open('w') as outfile:
        for line in infile:
            entry = json.loads(line)
            processed = process_entry(entry)
            
            if processed:
                outfile.write(json.dumps(processed) + '\n')
                sleep(1)  # Rate limiting

# Example usage
create_prompt_dataset(
    input_path='manim_full_reference.jsonl',
    output_path='manim_ollama_full_reference.jsonl'
)