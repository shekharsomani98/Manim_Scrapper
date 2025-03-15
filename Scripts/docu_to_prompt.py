import json
from pathlib import Path

def process_entry(entry):
    """Extract function name and description for each function in the entry"""
    functions = entry.get('functions', [])
    source = entry.get('source_link', '')
    
    pairs = []
    for func in functions:
        name = func.get('name', '').split('[')[0].strip()  # Remove [source] suffix
        description = func.get('description', '').strip()
        
        if name and description:
            pairs.append({
                "prompt": name,
                "response": description,
                "source": source
            })
    
    return pairs

def convert_dataset(input_path, output_path):
    """Convert full dataset to function-level prompt-response pairs"""
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        for line in infile:
            entry = json.loads(line)
            pairs = process_entry(entry)
            for pair in pairs:
                outfile.write(json.dumps(pair) + '\n')
    
    print(f"Converted dataset saved to {output_path}")

# Usage
convert_dataset(
    input_path='manim_full_reference.jsonl',
    output_path='manim_function_prompt_response.jsonl'
)