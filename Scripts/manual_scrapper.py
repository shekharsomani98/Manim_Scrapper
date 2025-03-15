import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

BASE_URL = "https://docs.manim.community/en/stable/"
START_URL = urljoin(BASE_URL, "reference.html")

def get_page_content(url):
    """Fetch page content with error handling"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        # print(response.text)
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return None

def process_toc_node(node, dataset):
    """Recursively process TOC tree nodes"""
    if node.name == "li":
        a_tag = node.find('a', class_='reference internal')
        if a_tag and ('module' in a_tag.get('class', []) or 'reference' in a_tag.get('class', [])):
            entry_url = urljoin(BASE_URL, a_tag['href'])
            # Scrape module documentation
            entry = scrape_module_entry(entry_url)
            if entry:
                dataset.append(entry)
                print(f"Processed module: {entry['name']}")

    # Recursively process child elements
    if hasattr(node, 'children'):
        for child in node.children:
            process_toc_node(child, dataset)

def scrape_module_entry(url):
    """Scrape a module documentation page"""
    soup = get_page_content(url)
    if not soup or not soup.find('h1'):
        return None

    entry = {
        "name": soup.find('h1').text.strip(),
        "type": "module",
        "classes": [],
        "functions": [],
        "examples": [],
        "source_link": url
    }

    # Extract module description
    if desc := soup.find('div', class_='desc'):
        print(desc)
        entry["description"] = desc.get_text(' ', strip=True)

    # Extract classes and functions
    for item in soup.find_all('dl', class_=['class', 'function']):
        class_func = {
            "name": item.dt.get_text().strip(),
            "type": item['class'][0],
            "description": item.dd.get_text(' ', strip=True) if item.dd else ""
        }
        if item['class'][0] == 'class':
            entry["classes"].append(class_func)
        else:
            entry["functions"].append(class_func)

    # Extract code examples
    for example in soup.select('div.highlight-python'):
        code = example.find('pre').get_text().strip()
        entry["examples"].append({
            "code": code,
            "context": get_example_context(example)
        })

    return entry

def get_example_context(example):
    """Get preceding paragraphs for example context"""
    context = []
    prev = example.find_previous_sibling()
    while prev and prev.name in ['p', 'div']:
        context.insert(0, prev.get_text(' ', strip=True))
        prev = prev.find_previous_sibling()
    return " ".join(context[:2])

def scrape_reference_entry(url):
    """Scrape individual reference entry page"""
    soup = get_page_content(url)
    if not soup:
        return None
    
    entry = {
        "name": soup.find('h1').text.strip(),
        "type": "class" if "class" in url else "function",
        "description": "",
        "parameters": [],
        "examples": [],
        "source_link": url
    }
    
    # Extract description
    if desc := soup.find('dd'):
        entry["description"] = desc.get_text(' ', strip=True)
    
    # Extract parameters
    for param in soup.select('dl.field-list dt'):
        param_name = param.text.strip()
        param_desc = param.find_next('dd').text.strip()
        entry["parameters"].append({
            "name": param_name,
            "description": param_desc
        })
    
    # Extract code examples
    for example in soup.select('div.highlight-python'):
        code = example.find('pre').text.strip()
        entry["examples"].append({
            "code": code,
            "context": " ".join([p.text for p in example.find_previous_all('p')][-2:])
        })
    
    return entry

def scrape_full_reference():
    dataset = []
    main_soup = get_page_content(START_URL)
    
    # Find the main documentation TOC
    toc = main_soup.find('div', class_='toctree-wrapper')
    # print(toc)
    process_toc_node(toc, dataset)
    
    # Save results
    with open('manim_full_reference.jsonl', 'w') as f:
        for item in dataset:
            f.write(json.dumps(item) + '\n')
    
    print(f"Scraped {len(dataset)} entries!")
    return dataset

# Run the scraper
scrape_full_reference()