import json
import re
import html

INPUT_FILE = r"C:\Users\smith\Documents\SMITH\College\MCA\II-Semester\Internship\Adiyen\Task\Task 2\B3\json\THE PRINCIPAL UPANISADS.json"
OUTPUT_FILE = "task2_chunked_output.json"

CHUNK_SIZE = 2000
OVERLAP = 400
MIN_CHUNK_SIZE = 300  # avoid very tiny chunks


def clean_text(text):
    # unescape html entities
    text = html.unescape(text)

    # remove html tags like <i>...</i>, <sup>...</sup>
    text = re.sub(r"<[^>]+>", "", text)

    # normalize line breaks
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # fix hyphenated line-break words: "con-\nduct" -> "conduct"
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)

    # join remaining newlines as spaces
    text = re.sub(r"\n+", " ", text)

    # fix missing spaces after punctuation
    text = re.sub(r"([.!?;:])([A-Za-z])", r"\1 \2", text)

    # fix words stuck together in common OCR cases
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)

    # normalize multiple spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def split_into_sentences(text):
    # sentence split
    sentences = re.split(r'(?<=[.!?])\s+', text)

    cleaned = []
    for s in sentences:
        s = s.strip()
        if s:
            cleaned.append(s)
    return cleaned


def sentence_chunk(text, chunk_size=2000, overlap=400, min_chunk_size=300):
    sentences = split_into_sentences(text)
    chunks = []

    i = 0
    while i < len(sentences):
        current = []
        current_len = 0
        j = i

        # build chunk with complete sentences only
        while j < len(sentences):
            sent = sentences[j]
            extra = len(sent) + (1 if current else 0)

            if current_len + extra <= chunk_size:
                current.append(sent)
                current_len += extra
                j += 1
            else:
                break

        # if one sentence itself is too large
        if not current and j < len(sentences):
            current = [sentences[j]]
            j += 1

        chunk_text = " ".join(current).strip()

        # merge tiny अंतिम chunk into previous chunk
        if chunks and len(chunk_text) < min_chunk_size:
            merged = chunks[-1] + " " + chunk_text
            if len(merged) <= chunk_size + overlap:
                chunks[-1] = merged.strip()
            else:
                chunks.append(chunk_text)
            break
        else:
            chunks.append(chunk_text)

        # build overlap using full sentences from end of current chunk
        overlap_sents = []
        overlap_len = 0

        for sent in reversed(current):
            add_len = len(sent) + (1 if overlap_sents else 0)
            if overlap_len + add_len <= overlap:
                overlap_sents.insert(0, sent)
                overlap_len += add_len
            else:
                break

        next_i = j - len(overlap_sents)

        # safety: always move forward
        if next_i <= i:
            next_i = i + 1

        i = next_i

    # remove accidental duplicate consecutive chunks
    deduped = []
    for ch in chunks:
        if not deduped or deduped[-1] != ch:
            deduped.append(ch)

    return deduped


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

output = []

for item in data:
    raw_text = item.get("chunk", "")
    ref = item.get("ref", "").strip()

    text = clean_text(raw_text)
    if not text:
        continue

    chunks = sentence_chunk(
        text,
        chunk_size=CHUNK_SIZE,
        overlap=OVERLAP,
        min_chunk_size=MIN_CHUNK_SIZE
    )

    for ch in chunks:
        output.append({
            "chunk": ch,
            "ref": ref
        })

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("✅ Fixed chunked JSON created successfully")
print("Total chunks:", len(output))