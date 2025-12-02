from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from openai import OpenAI
from utils import *
import pandas as pd
import os

data_dir = ".."

clusters_path = os.path.join(data_dir, "other_outputs", "revision_clusters_sorted.csv")
clusters = pd.read_csv(clusters_path)

client = OpenAI(api_key=OPENAI_API_KEY)


def name_technique(analysis, model="gpt-4o-mini"):
    """
    analysis: str or list of str
        Textual analysis to summarize.
    model: choose any OpenAI model, default is fast & cheap
    
    Returns: designated category name.
    """

    prompt = f"""
    You are an expert in political narratives, conflict studies, and cultural heritage.
    You are currently investigating revisions on Wikipedia articles for potential weaponization of cultural heritage topics.
    The below is the analysis of one such revision already made earlier in the pipeline. It is a given that the original revision has employed weaponization.
    Your task is to choose, among the given list of weaponization techniques, the ONE most likely weaponization technique the original revision employed.
    Full list of weaponization techniques to choose from as well as their exact definition in this context (LIMITED TO THESE OPTIONS, NO OTHER):
            "Terminology Manipulation": Swapping neutral or standard terms (for names, titles, exonyms, etc.) for loaded alternatives
            "Euphemism and Doublespeak": Replacing direct language with softer phrasing to obscure meaning
            "Selective Omission": Deleting inconvenient facts, dates, or events to skew the narrative
            "Selective Insertion": Adding one-sided or fringe claims that favor a particular agenda
            "Article Structure Manipulation": Reordering or restructuring the article text itself to manipulate interpretation
            "Source Biasing": Replacing reputable citations with partisan or unverifiable ones
            "Citation Washing": Bulk-adding irrelevant or low-quality citations to fake credibility
            "Citation Deletion": Removing citations to make opposing views appear less verifiable
            "Image and Media Manipulation": Specifically using maps, images, or video media to reinforce a viewpoint
            "Glorification": Portraying own or friendly subjects as more heroic, justified, and righteous, etc. via loaded and emotionally appealing language
            "Villification": Portraying opposing subjects to oneself/"enemies" as more evil, wicked, barbaric, etc. via loaded and emotionally appealing language
            "Timeline Rewriting": Shifting dates or sequences to alter causality or responsibility

    Analysis of the revision to categorize: {analysis}

    Answer ONLY with the name of the chosen technique exactly as is - NO explanations or definitions.
    """

    response = client.responses.create(
        model=model,
        input=prompt
    )
    # make sure there is no quotation marks or extra spaces
    result = response.output_text.strip().replace('"', '').replace("'", "")
    #print("Category: ", result, ". Original analysis: ", analysis)
    
    return result


# Copy to new DataFrame
clusters_new = clusters.copy()[['cluster', 'source', 'original_text']]

# Function to apply
def process_text(text):
    return name_technique(text)

# Create executor and run with tqdm
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(tqdm(executor.map(process_text, clusters_new['original_text']), total=len(clusters_new)))

# Assign back to DataFrame
clusters_new['weaponization_technique'] = results

output_directory = os.path.join(data_dir, "other_outputs", "weaponization_analysis")
os.makedirs(output_directory, exist_ok=True)
output_path = os.path.join(output_directory, "clusters_with_weaponization_techniques.csv")
clusters_new.to_csv(output_path, index=False)
print(f"Saved the analysis results to {output_path}")

