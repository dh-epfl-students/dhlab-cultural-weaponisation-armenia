import json
from openai import OpenAI
import os
import sys
import difflib
import concurrent.futures

#sys.path.append('../')
from utils import *

input_directory = "../enriched_sample_subset"
output_directory = "../txt_results"
os.makedirs(output_directory, exist_ok=True)


client = OpenAI(api_key=OPENAI_API_KEY)


def load_jsonl(filepath):
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records

def parse_unidiff(diff_text):
    added_lines, removed_lines, word_added, word_removed = [], [], [], []
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

def detect_weaponisation(record):
    if record.get("version") == "diff":
        diff_text = record.get("Diff", "")
        added_lines, removed_lines, word_added, word_removed = parse_unidiff(diff_text)
        record["Added_Lines"] = added_lines
        record["Removed_Lines"] = removed_lines
        record["Added_Words"] = word_added
        record["Removed_Words"] = word_removed

    record_json = json.dumps(record, indent=2, ensure_ascii=False)

    prompt = f"""
You are an expert linguistic analysis assistant specializing in detecting subtle shifts in language that might be used to weaponize cultural heritage.

The input is a JSON record representing a Wikipedia article revision. The record follows one of these structures:
1. For the original article version (version "first_version"):
   {{
     "version": "first_version",
     "Content": "<full article text>"
   }}
2. For a revision (version "diff"):
   {{
     "version": "diff",
     "Timestamp": "<ISO timestamp>",
     "User": "<editor identifier>",
     "Comment": "<revision comment>",
     "Diff": "<original textual diff in unified diff format>"
     "Added_Lines": [<list of lines outright added>],
     "Removed_Lines": [<list of lines outright removed>],
     "Added_Words": [<list of words added in modified sentences>],
     "Removed_Words": [<list of words removed in modified sentences>]
   }}

⚠️ Important Instructions:
- If the version is "diff", focus primarily on the Added_Lines, Removed_Lines, Added_Words, and Removed_Words fields, i.e. on the lines (and words) actually added or deleted (i.e. not the lines that are untouched) as well as whatever additional context provided by the "User" and "Comment" fields.
- Ignore lines in the Diff field that have no prefix — these are unchanged context.
- Do not evaluate unchanged paragraphs for weaponization unless they were modified.
- For an original version (version "first_version"), treat it as baseline text.
- Analyze the text for subtle shifts in tone, style, or content that may be used to weaponize cultural heritage.

Below are examples of weaponisation terms and narratives:
• Term (Armenian Perspective):
  - "Armenian Genocide" (vs "alleged" or "disputed" genocide)
  - "Historical Armenian lands" / "Western Armenia"
  - "Cultural erasure of Armenians in Nakhichevan"
  - "Destruction of khachkars in Julfa"
  - "Ethnic cleansing of Armenians from Artsakh"
  - "Ancient Armenian monasteries in present-day Turkey"
  - "Armenian heritage sites under Azerbaijani control"
  - "Forced demographic changes in Nagorno-Karabakh"
• Term (Turkish/Azerbaijani/Rival Perspective):
  - "So-called Armenian Genocide"
  - "Turkish–Armenian relocation" / "1915 deportations"
  - "Caucasian Albanian heritage" (used to reattribute Armenian sites)
  - "Illegal occupation of Karabakh by Armenia"
  - "Liberation of Azerbaijani lands"
  - "Fabricated Armenian claims"
  - "Armenian aggression"
  - "Armenian terrorism" (used to describe ASALA/other groups)
  - "Destruction of Azerbaijani cultural sites by Armenians"
Implication or consequence: These terms may be used to justify actions, shift narratives, or frame cultural or territorial control in a specific light.

Using these examples as guidance, please provide a clear Judgment ("Weaponised" or "Not Weaponised" (if the change is grammatical, stylistic, or unrelated to cultural/political narratives)) along with a brief Explanation citing specific linguistic indicators from the "+" or "-" lines only.
Note that each entry might not strictly immediately follow prior ones, so only judge the entry by its own merit.

Here is the input JSON:
{record_json}

Your analysis:
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a neutral linguistic analysis expert focused on detecting weaponization of cultural heritage."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error during API call: {e}"

def analyze_file(input_file):
    records = load_jsonl(input_file)
    print(f"[{input_file}] Loaded {len(records)} records.")
    results = []

    for idx, record in enumerate(records, start=1):
        analysis = detect_weaponisation(record)
        print(analysis)
        results.append(f"Record {idx} (Version: {record.get('version', 'N/A')}):\n{analysis}\n{'-'*80}\n")
        print(f"[{input_file}] Processed record {idx}/{len(records)}")
    return (input_file, results)

def save_analysis_result(file_path, results):
    base_name = os.path.splitext(os.path.basename(file_path))[0].replace("_enriched", "")
    output_file = f"{output_directory}/{base_name}_analysis.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(results)
    print(f"[{file_path}] Saved analysis to {output_file}")

# ----------------------------
# Threaded Execution Section
# ----------------------------

jsonl_files = [
    os.path.join(input_directory, f)
    for f in os.listdir(input_directory)
    if f.endswith(".jsonl")
]


with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    future_to_file = {executor.submit(analyze_file, f): f for f in jsonl_files}

    for future in concurrent.futures.as_completed(future_to_file):
        input_file, results = future.result()
        save_analysis_result(input_file, results)
