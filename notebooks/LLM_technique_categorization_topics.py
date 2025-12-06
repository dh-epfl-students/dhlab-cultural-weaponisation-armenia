from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from openai import OpenAI
from utils import *
import pandas as pd
import os

data_dir = ".."

topics_path = os.path.join(data_dir, "other_outputs", "entries_exclusive_to_general_topics.csv")
topics = pd.read_csv(topics_path)

client = OpenAI(api_key=OPENAI_API_KEY)


def name_technique(analysis, model="gpt-4o-mini"):
    """
    analysis: str or list of str
        Textual analysis to summarize.
    model: choose any OpenAI model, default is fast & cheap
    
    Returns: designated category name.
    """
   
    # removed for now due to overlap with the other categories:
    # "Image and Media Manipulation": Specifically using either images, videos, maps and other types of similar media, etc. or information (captions etc.) embedded in them to reinforce or trivialize a viewpoint. Example: 

    prompt = f"""
    You are an expert in political narratives, conflict studies, and cultural heritage.
    You are currently investigating revisions on Wikipedia articles for potential weaponization of cultural heritage topics.
    The below is the analysis of one such revision already made earlier in the pipeline. It is a given that the original revision has employed weaponization.
    Your task is to choose, among the given list of weaponization techniques, the ONE most likely weaponization technique the original revision employed.
    Full list of weaponization techniques to choose from as well as their exact definition (and example) in this context (LIMITED TO THESE OPTIONS, NO OTHER):
            "Terminology Biasing": Swapping neutral, or standard, or slanted-towards-one-side terms (for names, titles, exonyms, etc.) for alternatives culturally/ideologically slanted towards another side. Examples: "Armenian Genocide" vs. "Armenian Relocation" vs. "so-called Armenian Genocide", etc.
            "Euphemism and Doublespeak": Replacing direct language with softer phrasing to obscure meaning. Example: revision changing "official state denial of the Armenian Genocide" to "that is considered by many historians as official state denial of the Armenian Genocide", or revision changing "denying the Armenian Genocide" to "disputing the appropriateness of the Genocide label." 
            "Selective Omission": Deleting inconvenient facts, dates, or events in the text proper to skew the narrative. Example: revision deleting significant passage that details the rounding up and imprisonment of Armenian intellectuals during the events of April 1915, or revision removing the line `[[Category:Genocides in Asia]]` when it comes to the Armenian Genocide article.
            "Selective Insertion": Adding one-sided or fringe claims/ facts in the text proper that favor a particular agenda. Example: revision adding "===Websites supporting the genocide theses===" including an entire series of links to pro-Armenian websites; or revision claiming that "No Turkish state official has visited Tsitsernakaberd.".
            "Source Biasing": Replacing reputable citations with partisan (no matter how verifiable or otherwise) ones. Example: revision replacing a reference to a source that provided a more general context about the Armenian Genocide with a specific citation from Dennis Papazian's book, "What Every Armenian Should Know."
            "Citation Washing": Bulk-adding irrelevant or low-quality citations to fake credibility. Example: adding multiple low-quality sources (e.g., blogs, self-published sources, etc.) to support Turkish/Armenian claims.
            "Citation Deletion": Removing citations to make opposing views appear less verifiable. Example: removing a citation to Michael M. Gunter's work on "Armenian Terrorism" by claiming him as a "genocide denialist" without evidence.
            "Tag Manipulation": Adding or removing specific Wikipedia tags (e.g., "neutrality disputed", "citation needed", etc.) to influence readers' perception of the article's credibility or bias. Example: revisions adding or removing "neutral point of view" tags on articles related to the Armenian Genocide, or addition/removal of the "msg:TotallyDisputed" tag, among others.
            "Glorification & Vilification": Portraying own or friendly subjects as more heroic, justified, and righteous, etc; and/or Portraying opposing subjects to oneself/"enemies" as more evil, wicked, barbaric, etc.; via loaded and emotionally appealing language. Examples: revision claiming that Armenians "were mean people and hated americans."; or revisions adding references to "MASSACRE BY TURKS IN CAUCASUS TOWNS" and in the process highlight Turkish atrocities while emotionally highlighting Armenian victimhood. 
            "Timeline Rewriting": Shifting dates or sequences to alter causality or responsibility. Example: revision changing changes the date range of the Armenian Genocide from "1915-1916" to "1915-1922.", or revision changing the April 24 arrest of Armenian intellectuals in 1915 from as simple "an event during the Armenian Genocide" to "the first major event of the Armenian Genocide".

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
topics_new = topics.copy()[['topic', 'source', 'original_text']]

# Function to apply
def process_text(text):
    return name_technique(text)

# Create executor and run with tqdm
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(tqdm(executor.map(process_text, topics_new['original_text']), total=len(topics_new)))

# Assign back to DataFrame
topics_new['weaponization_technique'] = results

output_directory = os.path.join(data_dir, "other_outputs", "weaponization_analysis")
os.makedirs(output_directory, exist_ok=True)
output_path = os.path.join(output_directory, "topics-exclusive_with_weaponization_techniques.csv")
topics_new.to_csv(output_path, index=False)
print(f"Saved the analysis results to {output_path}")

