import re
import json

# Book name
BOOK_NAME = "966.ignca-19284-rb_Part_2"

# Path to the processed txt file
TXT_PATH = r"C:\Users\smith\Documents\SMITH\College\MCA\II-Semester\Internship\Adiyen\Task\Task 4\B7\processed\surya_ocr_966.ignca-19284-rb_Part_2.txt"

with open(TXT_PATH, "r", encoding="utf-8") as f:
    text = f.read()

# Regex to find all chapter headers and their content
chapter_pattern = re.compile(
    r'chapter:\s*([^\n]+)\n(.*?)(?=\nchapter:|\Z)',
    re.DOTALL | re.IGNORECASE
)

structured_chunks = []

matches = chapter_pattern.findall(text)
print(f"✅ Found {len(matches)} chapters")

for chapter_name, chapter_content in matches:
    # Split content into paragraphs (non-empty lines separated by blank lines)
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', chapter_content) if p.strip()]
    for para in paragraphs:
        structured_chunks.append({
            "chunk": para,
            "ref": f"{BOOK_NAME} -> {chapter_name.strip()}"
        })

# Save JSON
with open('structured_book_chunks.json', 'w', encoding='utf-8') as json_file:
    json.dump(structured_chunks, json_file, ensure_ascii=False, indent=2)

print(f"✅ Successfully created {len(structured_chunks)} structured chunks in structured_book_chunks.json")
