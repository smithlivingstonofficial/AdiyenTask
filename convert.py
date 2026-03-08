import json
import re
import os

def process_verse_file(input_path, output_path):
    print(f"Reading file: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Extract Chapter Name
    # Look for 'chapter:' at the beginning (case insensitive)
    chapter_match = re.search(r'^chapter:\s*(.+)', content, re.IGNORECASE)
    if chapter_match:
        chapter_name = chapter_match.group(1).strip()
        # Remove the header line(s) to process the rest of the text
        content_body = content[chapter_match.end():]
    else:
        chapter_name = "Unknown Chapter"
        content_body = content

    # 2. Derive Book Name from Filename
    # Assuming filename '6860.txt' -> book name '6860'
    base_name = os.path.basename(input_path)
    book_name = os.path.splitext(base_name)[0]

    # 3. Split into Blocks based on Spacing
    # User requirement: "consider for the new like spacing" -> Split by blank lines
    blocks = re.split(r'\n\s*\n', content_body.strip())
    # Filter empty blocks
    blocks = [b.strip() for b in blocks if b.strip()]

    output_data = []

    # Mapping for Devanagari digits to standard digits
    dev_digits = "०१२३४५६७८९"
    eng_digits = "0123456789"
    digit_map = str.maketrans(dev_digits, eng_digits)

    # Regex to identify a block ending with verse numbers (e.g., ||7|| or ||20||21||)
    # Matches '||' or '॥', followed by digits, possibly repeated
    # Captures the entire footer string ending with the block
    footer_pattern = re.compile(r'((?:[\u0965|]+\s*[०-९0-9]+\s*)+[\u0965|]+)\s*$')
    
    # Helper to extract list of integers from footer string
    def parse_numbers(footer_str):
        # Find all number groups
        nums = re.findall(r'[०-९0-9]+', footer_str)
        # Convert to standard digit strings, strip leading zeros if int conversion desired
        return [str(int(n.translate(digit_map))) for n in nums]

    # State variables
    pending_verses = [] # List of dicts, each has 'text' and 'nums' (as list)
    current_intro = []  # List of intro paragraphs

    for block in blocks:
        match = footer_pattern.search(block)
        
        if match:
            # Block ends with numbers -> Verse or Commentary
            footer_str = match.group(1)
            block_nums = parse_numbers(footer_str)
            
            # --- LOGIC: IS THIS A COMMENTARY? ---
            # Check if 'block_nums' matches the numbers of the *latest* pending verses.
            # Usually commentary covers the immediately preceding verses.
            
            # Flat list of all pending verse numbers
            pending_nums_flat = []
            for v in pending_verses:
                pending_nums_flat.extend(v['nums'])
            
            is_commentary_match = False
            matched_verses_count = 0
            
            # Check for suffix match
            if pending_nums_flat and len(pending_nums_flat) >= len(block_nums):
                suffix = pending_nums_flat[-len(block_nums):]
                if suffix == block_nums:
                    is_commentary_match = True
                    
                    # Determine how many pending verse *entries* cover these numbers
                    nums_needed = len(block_nums)
                    covered = 0
                    count = 0
                    for i in range(len(pending_verses) - 1, -1, -1):
                        covered += len(pending_verses[i]['nums'])
                        count += 1
                        if covered >= nums_needed:
                            break
                    matched_verses_count = count

            if is_commentary_match:
                # --- CASE: COMMENTARY ---
                # 1. Flush any orphan verses (those before the matched group)
                orphans = pending_verses[:-matched_verses_count] if matched_verses_count < len(pending_verses) else []
                for orphan in orphans:
                    ref_str = f"{book_name} -> {chapter_name} -> {orphan['nums'][0]}"
                    output_data.append({
                        "dev_verse": orphan['text'],
                        "commentary": "", # No commentary found
                        "ref": ref_str
                    })
                
                # 2. Process the matched group
                matched_group = pending_verses[-matched_verses_count:]
                
                # Combine multiple verses if grouped
                full_verse_text = "\n\n".join([v['text'] for v in matched_group])
                
                # Use the starting verse number for the reference
                ref_num = matched_group[0]['nums'][0]
                ref_str = f"{book_name} -> {chapter_name} -> {ref_num}"
                
                output_data.append({
                    "dev_verse": full_verse_text,
                    "commentary": block,
                    "ref": ref_str
                })
                
                # Reset buffers
                pending_verses = []
                current_intro = []
                
            else:
                # --- CASE: NEW VERSE ---
                # Not a match for existing pending verses -> Treat as new Verse
                
                # Check if we have pending verses that are now effectively orphans?
                # No, wait until we find a match or finish.
                # Verses might just be stacking up (e.g. Verse 20, Verse 21... then Comm 20-21).
                
                verse_text = block
                if current_intro:
                    # Prepend intro text
                    intro_text = "\n\n".join(current_intro)
                    verse_text = intro_text + "\n\n" + block
                    current_intro = [] # Reset intro
                
                pending_verses.append({
                    'text': verse_text,
                    'nums': block_nums
                })
        else:
            # --- CASE: INTRO / OTHER ---
            # No numbers found. Treat as introductory text for the *next* verse.
            current_intro.append(block)

    # End of Loop: Flush any remaining pending verses as orphans
    for orphan in pending_verses:
        ref_str = f"{book_name} -> {chapter_name} -> {orphan['nums'][0]}"
        output_data.append({
            "dev_verse": orphan['text'],
            "commentary": "",
            "ref": ref_str
        })

    # Write JSON output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)
        
    print(f"Successfully processed '{input_path}'.")
    print(f"Created '{output_path}' with {len(output_data)} entries.")

if __name__ == "__main__":
    # Input and Output paths
    INPUT_FILE = r"c:\Users\smith\Documents\SMITH\College\MCA\II-Semester\Internship\Adiyen\Task\B1-6860\processed\6860.txt"
    OUTPUT_FILE = "output_6860.json"
    
    if os.path.exists(INPUT_FILE):
        process_verse_file(INPUT_FILE, OUTPUT_FILE)
    else:
        print(f"Error: Input file not found at {INPUT_FILE}")
