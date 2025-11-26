import os
import json
import difflib
from concurrent.futures import ThreadPoolExecutor, as_completed

input_directory = "revisions_new"
output_directory = "csv_results"
os.makedirs(output_directory, exist_ok=True)

def load_jsonl(filepath):
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records

def save_jsonl(filepath, records):
    with open(filepath, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

def parse_unidiff(diff_text):
    added_lines = []
    removed_lines = []
    word_added = []
    word_removed = []

    lines = diff_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith(('@@', '---', '+++')):
            i += 1
            continue

        if line.startswith('-'):
            removed_line = line[1:].strip()

            if i + 1 < len(lines) and lines[i + 1].startswith('+'):
                added_line = lines[i + 1][1:].strip()
                diff = difflib.ndiff(removed_line.split(), added_line.split())
                for word in diff:
                    if word.startswith('+ '):
                        word_added.append(word[2:])
                    elif word.startswith('- '):
                        word_removed.append(word[2:])
                i += 2
            else:
                removed_lines.append(removed_line)
                i += 1

        elif line.startswith('+'):
            added_lines.append(line[1:].strip())
            i += 1
        else:
            i += 1

    return added_lines, removed_lines, word_added, word_removed

def process_record(record):
    if record.get("version") == "diff":
        diff_text = record.get("Diff", "")
        added_lines, removed_lines, word_added, word_removed = parse_unidiff(diff_text)
        record["Added_Lines"] = added_lines
        record["Removed_Lines"] = removed_lines
        record["Added_Words"] = word_added
        record["Removed_Words"] = word_removed
    return record

def process_file(file_path):
    try:
        records = load_jsonl(file_path)
        updated_records = [process_record(record) for record in records]

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file = os.path.join(output_directory, f"{base_name}_enriched.jsonl")
        save_jsonl(output_file, updated_records)
        print(f"[✓] Processed: {base_name}")
    except Exception as e:
        print(f"[!] Failed on {file_path}: {e}")

# ---------------------------
# Thread Pool Executor
# ---------------------------
jsonl_files = [
    os.path.join(input_directory, f)
    for f in os.listdir(input_directory)
    if f.endswith(".jsonl")
]

with ThreadPoolExecutor(max_workers=12) as executor:
    futures = [executor.submit(process_file, file_path) for file_path in jsonl_files]
    for _ in as_completed(futures):
        pass  # progress is printed in process_file
