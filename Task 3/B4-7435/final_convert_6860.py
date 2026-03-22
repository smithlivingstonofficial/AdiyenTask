import json
import re
import os

def devanagari_to_arabic(text):
    dev_map = {
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
        '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
    }
    return "".join([dev_map.get(c, c) for c in text])

def extract_number(text):
    # Matches a number at the very end of the string, optionally surrounded by pipes/lines
    # Pattern: Digit sequence, optional whitespace/dandas, End of String
    match = re.search(r'([०-९0-9]+)\s*[\|॥।]*\s*$', text)
    if match:
        return devanagari_to_arabic(match.group(1))
    return None

def parse_file(input_path, output_path):
    print(f"Processing: {input_path}")
    if not os.path.exists(input_path):
        print(f"Error: File not found {input_path}")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into blocks by empty lines (2 or more newlines)
    # This separates paragraphs/verses
    blocks = re.split(r'\n\s*\n', content)
    
    data_map = {}
    order_keys = []
    
    current_book = "Unknown Book"
    current_chapter = "Unknown Chapter"
    current_verse_num = "0"
    
    # Markers
    MARKER_COMM = "भा०टी०"
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
            
        lines = block.split('\n')
        cleaned_lines = []
        
        # Extract headers and clean lines of the block
        header_found = False
        for line in lines:
            line_stripped = line.strip()
            # Check for Book
            if re.match(r'^book:', line_stripped, re.IGNORECASE):
                current_book = line_stripped.split(':', 1)[1].strip()
                header_found = True
            # Check for Chapter
            elif re.match(r'^chapter:', line_stripped, re.IGNORECASE):
                current_chapter = line_stripped.split(':', 1)[1].strip()
                header_found = True
            else:
                # Keep the line (stripped to remove outer whitespace, preserving content)
                if line_stripped:
                    cleaned_lines.append(line_stripped)
        
        content_text = "\n".join(cleaned_lines)
        if not content_text:
            continue
            
        # Extract Verse Number from this block
        # We assume the number is at the end of the block content
        extracted_num = extract_number(content_text)
        if extracted_num:
            current_verse_num = extracted_num
        
        # Prepare storage key
        key = (current_book, current_chapter, current_verse_num)
        if key not in data_map:
            data_map[key] = {"dev": [], "comm": []}
            order_keys.append(key)
            
        # Check for Commentary Split
        if MARKER_COMM in content_text:
            # Split only on first occurrence
            parts = content_text.split(MARKER_COMM, 1) 
            verse_part = parts[0].strip()
            # Add marker back to commentary for clarity
            comm_part = MARKER_COMM + " " + parts[1].strip() 
            
            if verse_part:
                data_map[key]["dev"].append(verse_part)
            if parts[1].strip(): # Only add if there is actual content
                data_map[key]["comm"].append(comm_part)
        else:
            # Whole block is treated as Verse content
            data_map[key]["dev"].append(content_text)
            
    # Build Final JSON
    json_output = []
    for key in order_keys:
        book, chapter, vnum = key
        entry = data_map[key]
        
        d_verse = "\n".join(entry["dev"]).strip()
        c_text = "\n".join(entry["comm"]).strip()
        
        # Avoid empty entries
        if not d_verse and not c_text:
            continue

        item = {
            "dev_verse": d_verse,
            "commentary": c_text,
            "ref": f"{book} -> {chapter} -> {vnum}"
        }
        json_output.append(item)
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, ensure_ascii=False, indent=4)
    print(f"Successfully converted {len(json_output)} items to {output_path}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths
    input_file = os.path.join(script_dir, "processed", "7435.txt")
    output_file = os.path.join(script_dir, "json", "7435.json")
    
    parse_file(input_file, output_file)
