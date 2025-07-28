import os
import sys
import json
import re
from collections import Counter
import fitz  # PyMuPDF


def clean_text(text):
    # Remove repeated characters (e.g., Reeeequest → Request)
    text = re.sub(r'(.)\1{2,}', r'\1', text)
    # Remove repeated words (e.g., "RFP RFP RFP" → "RFP")
    words = text.split()
    seen = set()
    deduped_words = []
    for word in words:
        if word not in seen:
            deduped_words.append(word)
            seen.add(word)
    return " ".join(deduped_words).strip()


def group_lines_into_blocks(lines):
    if not lines:
        return []

    blocks = []
    current_block = [lines[0]]

    for i in range(1, len(lines)):
        prev = lines[i - 1]
        curr = lines[i]
        vertical_gap = curr['bbox'][1] - prev['bbox'][3]

        if vertical_gap < (prev['size'] * 0.3):
            current_block.append(curr)
        else:
            text = " ".join(line['text'] for line in current_block)
            y0 = min(line['bbox'][1] for line in current_block)
            blocks.append({
                "text": text,
                "size": current_block[0]['size'],
                "font": current_block[0]['font'],
                "is_bold": current_block[0]['is_bold'],
                "bbox": current_block[0]['bbox'],
                "page": current_block[0]['page'],
                "y0": y0
            })
            current_block = [curr]

    text = " ".join(line['text'] for line in current_block)
    y0 = min(line['bbox'][1] for line in current_block)
    blocks.append({
        "text": text,
        "size": current_block[0]['size'],
        "font": current_block[0]['font'],
        "is_bold": current_block[0]['is_bold'],
        "bbox": current_block[0]['bbox'],
        "page": current_block[0]['page'],
        "y0": y0
    })

    return blocks


def extract_structured_blocks(pdf_path):
    doc = fitz.open(pdf_path)
    all_blocks = []

    for page_num, page in enumerate(doc):
        lines_raw = page.get_text("dict", sort=True)['blocks']
        page_lines = []
        for block in lines_raw:
            if block['type'] == 0:
                for line in block['lines']:
                    span = line['spans'][0]
                    text = clean_text(" ".join(span['text'] for span in line['spans']).strip())
                    if not text:
                        continue
                    page_lines.append({
                        "text": text,
                        "size": round(span['size'], 2),
                        "font": span['font'],
                        "is_bold": "bold" in span['font'].lower(),
                        "bbox": line['bbox'],
                        "page": page_num + 1
                    })
        all_blocks.extend(group_lines_into_blocks(page_lines))

    doc.close()
    return all_blocks


def find_title(blocks_on_first_page):
    top_blocks = sorted(
        [b for b in blocks_on_first_page if len(b['text']) > 10],
        key=lambda b: (-b['size'], b['y0'])
    )
    for block in top_blocks:
        text = block['text']
        if ":" in text and len(text.split()) > 5:
            return text.strip()
    return top_blocks[0]['text'].strip() if top_blocks else ""


def classify_headings(blocks, title_text):
    headings = []
    seen = set()
    font_sizes = [b['size'] for b in blocks if b['size'] > 0]
    body_font = Counter(font_sizes).most_common(1)[0][0]
    heading_sizes = sorted([s for s in set(font_sizes) if s > body_font], reverse=True)
    size_to_level = {size: f"H{idx + 1}" for idx, size in enumerate(heading_sizes)}

    for block in blocks:
        text = block['text'].strip()
        size = block['size']
        if not text or text in seen or text in title_text or len(text) > 300:
            continue
        if text.count(".") > 5 and text.count(" ") > 10:
            continue

        # Numbered heading
        if re.match(r'^\d+(\.\d+)*\s+', text):
            level = f"H{min(text.count('.') + 1, 4)}"
        elif size in size_to_level:
            level = size_to_level[size]
        else:
            continue

        headings.append({
            "level": level,
            "text": text,
            "page": block['page'],
            "y0": block['y0']
        })
        seen.add(text)

    headings.sort(key=lambda h: (h['page'], h['y0']))
    for h in headings:
        del h['y0']
    return headings


def process_single_pdf(pdf_path):
    blocks = extract_structured_blocks(pdf_path)
    if not blocks:
        return None
    first_page_blocks = [b for b in blocks if b['page'] == 1]
    title = find_title(first_page_blocks)
    outline = classify_headings(blocks, title)
    return {"title": title, "outline": outline}


if __name__ == "__main__":
    input_dir = "input"
    output_dir = "output_jsons"
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            input_path = os.path.join(input_dir, filename)
            print(f"Processing {filename}...")
            result = process_single_pdf(input_path)
            if result:
                output_filename = os.path.splitext(filename)[0] + ".json"
                output_path = os.path.join(output_dir, output_filename)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)
                print(f"→ Saved: {output_filename}")
