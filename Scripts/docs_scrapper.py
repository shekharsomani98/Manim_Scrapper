import requests
from bs4 import BeautifulSoup
import json
import re

def scrape_manim_binder_examples():
    dataset = []
    url = "https://docs.manim.community/en/stable/examples.html"
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all pre tags with manim class annotations
    for pre in soup.find_all('pre', {'data-manim-classname': True}):
        class_name = pre['data-manim-classname']
        code = pre.get_text().strip()
        
        # Clean the code (remove line numbers and >>> prompts)
        clean_code = re.sub(r'^(\d+|\>\>\>)\s*', '', code, flags=re.MULTILINE)
        
        dataset.append({
            "prompt": class_name,
            "response": clean_code
        })
    
    # Save to JSONL
    with open('manim_binder_dataset.jsonl', 'w') as f:
        for item in dataset:
            f.write(json.dumps(item) + '\n')
    
    print(f"Scraped {len(dataset)} interactive examples!")
    print(f"Sample entry: {json.dumps(dataset[0], indent=2)}") if dataset else None

# Run the scraper
scrape_manim_binder_examples()