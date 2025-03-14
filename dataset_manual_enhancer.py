import json
import openai
import os
from time import sleep

# Initialize OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

def gpt4_prompt_generation(code, max_retries=3):
    """Generate high-quality prompt using GPT-4 with animation-specific instructions"""
    system_prompt = """You are a Manim animation expert. Analyze the provided Python code and create a concise, 
natural language prompt that describes the animation being created. Follow these rules:
1. Identify key visual elements (shapes, graphs, 3D objects)
2. Recognize transformations (rotations, fades, transforms)
3. Note mathematical concepts (equations, vectors, functions)
4. Mention animation sequence if multiple steps
5. Use format: <Verb> <subject> <action> [with/of <details>]
Example: "Animate a rotating cube that transforms into a sphere while showing coordinate axes"

Keep prompts under 20 words and avoid technical terms like 'class' or 'self'."""

    for attempt in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Manim code:\n{code}\n\nPrompt:"}
                ],
                temperature=0.2,
                max_tokens=50,
                top_p=0.95
            )
            return response.choices[0].message['content'].strip('"').split('\n')[0]
        except Exception as e:
            if attempt < max_retries - 1:
                sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"GPT-4 failed: {str(e)}")
                return "Generate Manim animation"

def enhance_dataset(input_path, output_path, batch_size=5):
    """Process dataset with GPT-4 prompt generation"""
    enhanced = []
    
    with open(input_path, 'r') as f:
        entries = [json.loads(line) for line in f]
    
    # Process in batches to manage rate limits
    for i in range(0, len(entries), batch_size):
        batch = entries[i:i+batch_size]
        
        for entry in batch:
            code = entry['response']
            try:
                new_prompt = gpt4_prompt_generation(code)
                enhanced.append({
                    "prompt": new_prompt,
                    "response": code,
                    "original_prompt": entry.get('prompt', ''),
                    "source": entry.get('source', '')
                })
            except Exception as e:
                print(f"Error processing entry {i}: {str(e)}")
        
        sleep(1)  # Add delay between batches
    
    # Save enhanced dataset
    with open(output_path, 'w') as f:
        for entry in enhanced:
            f.write(json.dumps(entry) + '\n')
    
    print(f"Generated {len(enhanced)} GPT-4 enhanced prompts")

# Usage
enhance_dataset(
    input_path='manim_final_dataset.jsonl',
    output_path='manim_gpt4_only_dataset.jsonl',
    batch_size=3  # Reduce if hitting rate limits
)