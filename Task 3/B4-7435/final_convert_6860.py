import json
import re
import os

def devanagari_to_arabic(text):
    dev_map = {
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
        '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
    }
    result = []
    for char in text:
        result.append(dev_map.get(char, char))
    return "".join(result)

def parse_file(input_path, output_path):
    print(f"Processing: {input_path}")
    if not os.path.exists(input_path):
        print(f"Error: File not found {input_path}")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Normalize line endings
    content = content.replace('\r\n', '\n')
    
    # Split into blocks by empty lines
    blocks = re.split(r'\n\s*\n', content)
    
    data = []
    
    # Initial identifiers
    current_book = None
    current_chapter = None
    
    # Regex patterns
    book_pattern = re.compile(r'^book:\s*(.+)', re.IGNORECASE)
    chapter_pattern = re.compile(r'^chapter:\s*(.+)', re.IGNORECASE)
    
    # Regex to find verse numbers. 
    # Matches delimiters like ||, ॥, or | followed by number, followed by delimiters.
    verse_num_pattern = re.compile(r'[\|॥।]+\s*([०-९0-9]+)(?:\s*[\|॥।]+)?')

    pending_verse = None

    for block in blocks:
        block = block.strip()
        if not block:
            continue
            
        # 1. Check for Book/Chapter headers in the block
        # Blocks might look like: "chapter: blah\n\nverse text" if splitting failed, 
        # or just "chapter: blah" if separate block.
        # We process line by line to extract headers.
        
        lines = block.split('\n')
        remaining_lines = []
        header_found_in_block = False
        
        for line in lines:
            line_stripped = line.strip()
            
            # Check Book
            b_match = book_pattern.match(line_stripped)
            if b_match:
                current_book = b_match.group(1).strip()
                header_found_in_block = True
                continue
                
            # Check Chapter
            c_match = chapter_pattern.match(line_stripped)
            if c_match:
                current_chapter = c_match.group(1).strip()
                header_found_in_block = True
                continue
            
            remaining_lines.append(line)
        
        # If the block was just headers, we are done with this block
        block_content = "\n".join(remaining_lines).strip()
        if not block_content:
            continue

        # 2. Identify if it is a Verse or Commentary
        # A verse usually ends with a number in double dandas.
        # We look for the pattern at the text level.
        
        # Using findall to see if there's a verse number at the end
        matches = verse_num_pattern.findall(block_content)
        
        is_verse = False
        verse_num = None
        
        if matches:
            # Check position? 
            # Usually verse number is at the very end.
            # Let's verify if the match is near the end of the string.
            # Or assume if it contains such a pattern, it is a verse.
            # The Commentary usually mentions numbers (like Verse 7 says ...), 
            # but verses END with "|| 7 ||". 
            # Let's check if the pattern is at the END of the block.
            
            # Using search with $ anchor logic or just checking last match location
            last_match_num = matches[-1]
            # Simple heuristic: if the block ends with typical verse delimiter structure
            if re.search(r'[\|॥।]+\s*[०-९0-9]+\s*[\|॥।]*\s*$', block_content):
                is_verse = True
                verse_num = devanagari_to_arabic(last_match_num)
        
        if is_verse:
            # Check if this is commentary for the SAME verse (ends with same number)
            # Use 'ref' to infer or just store the number separately
            
            # Logic: If pending_verse exists and its verse number matches current one
            if pending_verse and pending_verse.get("_v_num") == verse_num:
                 # It is commentary
                if pending_verse["commentary"]:
                    pending_verse["commentary"] += "\n\n" + block_content
                else:
                    pending_verse["commentary"] = block_content
            else:
                # New Verse
                # Save previous pending verse if any
                if pending_verse:
                    del pending_verse["_v_num"]
                    data.append(pending_verse)
                    pending_verse = None
                
                # Determine references
                # If book name not found in text, use filename
                if not current_book:
                    filename = os.path.basename(input_path)
                    current_book = os.path.splitext(filename)[0]
                    
                ch_ref = current_chapter if current_chapter else "Unknown Chapter"
                
                pending_verse = {
                    "dev_verse": block_content,
                    "commentary": "",
                    "ref": f"{current_book} -> {ch_ref} -> {verse_num}",
                    "_v_num": verse_num
                }
        else:
            # It is Commentary (or header residue if Logic 1 missed something)
            if pending_verse:
                if pending_verse["commentary"]:
                    pending_verse["commentary"] += "\n\n" + block_content
                else:
                    pending_verse["commentary"] = block_content
            else:
                # Text appearing before any verse?
                print(f"Warning: Text found before any verse (or orphan): {block_content[:50]}...")
                # Could be intro text. Ignore or attach to 'header'? 
                # For now, ignore as per strict "Verse -> Commentary" structure implication.
    
    # Append the last one
    if pending_verse:
        if "_v_num" in pending_verse:
            del pending_verse["_v_num"]
        data.append(pending_verse)
        
    # Write output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Successfully converted {len(data)} items to {output_path}")

if __name__ == "__main__":
    # Setup paths relative to script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "processed", "7435.txt")
    output_file = os.path.join(script_dir, "json", "7435.json")
    
    parse_file(input_file, output_file)
