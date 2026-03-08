import json
import re
import os
import glob

def parse_verses_from_file(file_path):
    print(f"Reading file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Normalize line endings
    content = content.replace('\r\n', '\n')

    # Prepare data structure
    verses_data = []
    
    # Extract book name from filename (e.g., '9252.txt' -> '9252')
    filename = os.path.basename(file_path)
    book_name = os.path.splitext(filename)[0]

    # Devanagari numerals to Latin numerals map
    dev_numerals = "०१२३४५६७८९"
    lat_numerals = "0123456789"
    trans_table = str.maketrans(dev_numerals, lat_numerals)

    # Regex to find verse endings:
    # Looks for double danda (|| or ॥), optional space, number, optional space, double danda, end of line.
    verse_pattern = re.compile(r'[\|॥]+\s*([०-९0-9]+)\s*[\|॥]+\s*$')

    # Split content into blocks by blank lines to separate verses from commentary chunks
    blocks = re.split(r'\n\s*\n', content)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # If a block has NO verse numbers, we assume it's a commentary block and skip it.
        if not verse_pattern.search(block):
            continue

        # Process lines in the verse block
        lines = block.split('\n')
        current_verse_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            match = verse_pattern.search(line)
            if match:
                # Verse ending found
                current_verse_lines.append(line)
                
                # Extract number
                raw_num = match.group(1)
                verse_num = raw_num.translate(trans_table)
                
                # Construct verse object
                verse_text = "\n".join(current_verse_lines)
                
                verses_data.append({
                    "book": book_name,
                    "verse": int(verse_num), 
                    "original": verse_text
                })
                
                # Reset buffer for next verse in the block
                current_verse_lines = []
            else:
                # Accumulate line (part of a multi-line verse)
                current_verse_lines.append(line)

    return verses_data

def main():
    # Recursively find .txt files in 'processed' folders
    search_pattern = os.path.join("**", "processed", "*.txt")
    files = glob.glob(search_pattern, recursive=True)
    
    if not files:
        files = glob.glob("*.txt")

    print(f"Found {len(files)} files to process.")

    for file_path in files:
        try:
            print(f"Processing: {file_path}")
            data = parse_verses_from_file(file_path)
            
            if data:
                # Save in sibling 'json' directory
                processed_dir = os.path.dirname(file_path)
                parent_dir = os.path.dirname(processed_dir)
                json_dir = os.path.join(parent_dir, 'json')
                
                # Create json dir if it doesn't exist
                if not os.path.exists(json_dir):
                    try:
                        os.makedirs(json_dir)
                    except:
                        pass
                
                if os.path.exists(json_dir):
                    output_name = os.path.splitext(os.path.basename(file_path))[0] + ".json"
                    output_path = os.path.join(json_dir, output_name)
                else:
                    output_name = f"output_{os.path.splitext(os.path.basename(file_path))[0]}.json"
                    output_path = output_name
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                
                print(f"SUCCESS: Saved {len(data)} verses to {output_path}")
            else:
                print(f"WARNING: No verses found in {file_path}")

        except Exception as e:
            print(f"ERROR processing {file_path}: {e}")

if __name__ == "__main__":
    main()
