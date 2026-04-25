# Verse

import json
import re
import os

def devanagari_to_arabic_num(text):
    dev_map = {
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
        '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
    }
    result = []
    for char in text:
        result.append(dev_map.get(char, char))
    return "".join(result)

def convert_txt_to_json(input_path, output_path):
    print(f"Starting conversion for: {input_path}")
    
    # Check if file exists
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Normalize newlines
    content = content.replace('\r\n', '\n')

    # Get the base filename without extension to use as Book Name
    # Example: 'processed/9252.txt' -> '9252'
    filename = os.path.basename(input_path)
    book_name = os.path.splitext(filename)[0]

    # Split by at least one empty line (two newlines)
    # The regex \n\s*\n matches a newline, optional whitespace, and another newline
    blocks = re.split(r'\n\s*\n', content)

    verses_list = []
    
    # Regex to find verse numbers like: || 1 ||, ॥ १॥, or ending with just the number
    # Captures the number inside the delimiters (danda, double danda, pipe)
    # Added single danda '।' to the character class
    # Made trailing delimiter optional to handle cases like '॥१९९' (missing closing danda)
    verse_num_pattern = re.compile(r'[\|॥।]+\s*([०-९0-9]+)(?:\s*[\|॥।]+)?')

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Look for all verse numbers in the block
        matches = verse_num_pattern.findall(block)
        if matches:
            # Take the last found number as the verse number for this block
            raw_num = matches[-1]
            # Convert to Arabic numerals
            verse_num = devanagari_to_arabic_num(raw_num)
            
            # Create the JSON object
            verse_obj = {
                "dev_verse": block,
                "ref": f"{book_name} -> {verse_num}"
            }
            verses_list.append(verse_obj)
        else:
            print(f"Warning: Could not extract verse number from block starting with: {block[:30]}...")
            # If structure is strict, maybe we should skip.
            # But let's include it to debug if needed, or skip?
            # User requirement implies strict format "take the verse from the next line...".
            # The regex ensures we only pick up valid ones.

    # Write to output JSON file
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(verses_list, f, ensure_ascii=False, indent=4)
    
    print(f"Successfully converted {len(verses_list)} verses to {output_path}")

if __name__ == "__main__":
    # Determine absolute paths based on script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "processed", "2668.txt")
    output_file = os.path.join(script_dir, "json", "2668.json")
    
    convert_txt_to_json(input_file, output_file)
