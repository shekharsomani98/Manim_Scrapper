import json
from pathlib import Path

def has_example(description):
    """Check if the description contains an example"""
    return "Examples" in description or "Example:" in description

def process_entry(entry):
    """Extract function name and description, filtering for examples"""
    response = entry.get('response', [])
    prompt = entry.get('prompt', '')
    
    pairs = []

    if has_example(response):
        pairs.append({
            "prompt": prompt,
            "response": response
        })
    
    return pairs

def convert_dataset(input_path, output_path):
    """Convert full dataset to function-level prompt-response pairs with examples"""
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        for line in infile:
            entry = json.loads(line)
            pairs = process_entry(entry)
            for pair in pairs:
                outfile.write(json.dumps(pair) + '\n')
    
    print(f"Filtered dataset saved to {output_path}")


convert_dataset(
    input_path='manim_ollama_function_examples_dataset.jsonl',
    output_path='manim_function_filter_examples_only.jsonl'
)