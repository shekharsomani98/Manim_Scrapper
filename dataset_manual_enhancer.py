import json
import requests
from time import sleep

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"

def ollama_prompt(code, model="llama3.2", max_retries=3):
    """Generate prompts using local Ollama model"""
    system_prompt = """You are a Manim animation expert. Analyze the provided Python code and create a concise, 
natural language prompt that describes the animation being created. Follow these rules:
1. Identify key visual elements (shapes, graphs, 3D objects)
2. Recognize transformations (rotations, fades, transforms)
3. Note mathematical concepts (equations, vectors, functions)
4. Mention animation sequence if multiple steps
5. Use format: <Verb> <subject> <action> [with/of <details>]
Example: "Animate a rotating cube that transforms into a sphere while showing coordinate axes"

Keep prompts under 20 words and avoid technical terms like 'class' or 'self'."""

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
    input_path='manim_function_prompt_response.jsonl',
    output_path='manim_ollama_function_examples_dataset.jsonl'
)