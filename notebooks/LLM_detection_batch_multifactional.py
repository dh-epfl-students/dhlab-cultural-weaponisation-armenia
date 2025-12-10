import json
from openai import OpenAI
import os
import sys
import difflib
import concurrent.futures
import pandas as pd

#sys.path.append('../')
from utils import *

input_directory = "../csv_files"
output_directory = "../txt_results_finegrained"
os.makedirs(output_directory, exist_ok=True)


client = OpenAI(api_key=OPENAI_API_KEY)


def load_csv(filepath):
    # Read CSV using pandas
    df = pd.read_csv(filepath, encoding="utf-8")

    # Normalize "Source" column
    df["Source"] = df["Source"].apply(
        lambda x: os.path.basename(x).replace("_enriched_subsampled.jsonl", "")
    )

    # Convert to list of dicts (matching original function’s output)
    records = df.to_dict(orient="records")
    return records



def detect_weaponisation(record):
    record_json = json.dumps(record, indent=2, ensure_ascii=False)

    prompt = f"""
You are an expert linguistic analysis assistant specializing in detecting subtle shifts in language that might be used to weaponize cultural heritage.

The input is a JSON record representing a Wikipedia article revision. The record follows this structure:
   {{
     "Source": "<original article name>",
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
- Focus primarily on the Added_Lines, Removed_Lines, Added_Words, and Removed_Words fields, i.e. on the lines (and words) actually added or deleted (i.e. not the lines that are untouched) as well as whatever additional context provided by the "User" and "Comment" fields.
- Ignore lines in the Diff field that have no prefix — these are unchanged context.
- Do not evaluate unchanged paragraphs for weaponization unless they were modified.
- Analyze the text for subtle shifts in tone, style, or content that may be used to weaponize cultural heritage.

Below are examples of weaponisation terms and narratives:
• Term (Pro-Armenian Perspective):
  - "Armenian Genocide" (vs "alleged" or "disputed" genocide)
  - "Historical Armenian lands" / "Western Armenia"
  - "Cultural erasure of Armenians in Nakhichevan"
  - "Destruction of khachkars in Julfa"
  - "Ethnic cleansing of Armenians from Artsakh"
  - "Ancient Armenian monasteries in present-day Turkey"
  - "Armenian heritage sites under Azerbaijani control"
  - "Forced demographic changes in Nagorno-Karabakh"
• Term (General Anti-Armenian aka Turkish/Azerbaijani/Rival Perspective):
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

Using these examples as guidance, and - given that the given entry has already been judged as containing weaponization by a prior pipeline - please provide a clear Judgment (either "Pro-Armenian" or "Anti-Armenian") along with a brief Explanation citing specific linguistic indicators from the "+" or "-" lines only.
Special note that for the purpose of this analysis, "Pro-Armenian" can also encompass anti-Turkish or anti-Azerbaijani or anti-any-other-Armenian-historical-rival stances, while "Anti-Armenian" can also encompass pro-Turkish or pro-Azerbaijani or pro-any-other-Armenian-historical-rival stances.
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
    records = load_csv(input_file)
    print(f"[{input_file}] Loaded {len(records)} records.")
    results = []

    for idx, record in enumerate(records, start=1):
        #print(record)
        if record["Judgment"].lower() == "weaponised":
            analysis = detect_weaponisation(record)
            print(analysis)
            results.append(f"Record {idx} (Version: {record.get('version', 'N/A')}):\n{analysis}\n{'-'*80}\n")
            print(f"[{input_file}] Processed record {idx}/{len(records)}")
    return (input_file, results)

def save_analysis_result(file_path, results):
    base_name = os.path.splitext(os.path.basename(file_path))[0].replace("_output", "")
    output_file = f"{output_directory}/{base_name}_finegrained_analysis.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(results)
    print(f"[{file_path}] Saved analysis to {output_file}")

# ----------------------------
# Threaded Execution Section
# ----------------------------

csv_files = [
    os.path.join(input_directory, f)
    for f in os.listdir(input_directory)
    if f.endswith(".csv")
]


with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    future_to_file = {executor.submit(analyze_file, f): f for f in csv_files}

    for future in concurrent.futures.as_completed(future_to_file):
        input_file, results = future.result()
        save_analysis_result(input_file, results)
