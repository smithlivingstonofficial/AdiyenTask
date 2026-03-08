
code = r'''import json
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

    # Regex to find verse endings: matches || Num || at end of string
    # Groups: 1=Number
    verse_pattern = re.compile(r'[\|॥]+\s*([०-९0-9]+)\s*[\|॥]+\s*$')

    # Split content into blocks by blank lines
    blocks = re.split(r'\n\s*\n', content)
    
    last_verse_entry = None

    for block in blocks:
        block = block.strip()
        if not block:
            continue
        
        match = verse_pattern.search(block)
        if match:
            # It IS a verse
            raw_num = match.group(1)
            verse_num_str = raw_num.translate(trans_table)
            
            # Create new entry
            # Ref format: "Book -> VerseNum" (As requested: "book and verse number is enough")
            ref_str = f"{book_name} -> {verse_num_str}"
            
            new_entry = {
                "dev_verse": block,
                "commentary": "",
                "ref": ref_str
            }
            verses_data.append(new_entry)
            last_verse_entry = new_entry
        else:
            # It is NOT a verse -> Assume Commentary
            if last_verse_entry is not None:
                # Append to last verse's commentary
                if last_verse_entry["commentary"]:
                    last_verse_entry["commentary"] += "\n\n" + block
                else:
                    last_verse_entry["commentary"] = block
            else:
                # This could be header info or intro text before the first verse.
                # Since we don't have a place to put it, we'll ignore it or log it.
                # In strict mode, we might want to attach it to the next verse? 
                # But 'verse new line commentary' implies text follows verse.
                print(f"Warning: Found text block at start (ignored/intro): {block[:20]}...")

    return verses_data

def main():
    # Identify files to process.
    # Recursively find .txt files in 'processed' folders
    search_pattern = os.path.join("**", "processed", "*.txt")
    files = glob.glob(search_pattern, recursive=True)
    
    # Fallback to current directory txt files if no structure found
    if not files:
        files = glob.glob("*.txt")

    print(f"Found {len(files)} files to process.")

    for file_path in files:
        try:
            print(f"Processing: {file_path}")
            data = parse_verses_from_file(file_path)
            
            if data:
                # Target json directory
                processed_dir = os.path.dirname(file_path)
                parent_dir = os.path.dirname(processed_dir)
                json_dir = os.path.join(parent_dir, 'json')
                
                if not os.path.exists(json_dir):
                    try:
                        os.makedirs(json_dir)
                    except:
                        pass
                
                if os.path.exists(json_dir):
                    output_name = os.path.splitext(os.path.basename(file_path))[0] + ".json"
                    output_path = os.path.join(json_dir, output_name)
                else:
                    # Fallback to root
                    output_name = f"output_{os.path.splitext(os.path.basename(file_path))[0]}.json"
                    output_path = output_name
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                
                print(f"SUCCESS: Saved {len(data)} verses to {output_path}")
            else:
                print(f"WARNING: No verses parsed in {file_path}")

        except Exception as e:
            print(f"ERROR processing {file_path}: {e}")

if __name__ == "__main__":
    main()
'''

with open('convert.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated convert.py")
