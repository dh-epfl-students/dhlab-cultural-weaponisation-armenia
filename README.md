![Python](https://img.shields.io/badge/python-3.11-blue.svg)

# Monitoring and Detecting Cultural Heritage Manipulation in Armenia
*A Data-Driven Approach to Analyzing Russia’s Digital Influence on Cultural Narratives*

## Overview
This repository contains code, documentation, and resources for a research project investigating Russia’s manipulation and weaponisation of cultural heritage in Armenia. By combining data mining, Wikipedia analysis, semantic retrieval, and LLM-assisted annotation, this project aims to detect, trace, and analyze narrative shifts, coordinated editorial activity, and ideological framing around Armenian cultural heritage.

The goal is to build a transparent, reproducible analytical framework supporting academic research, cultural preservation, and evidence‑based policy-making.

## Motivation
Cultural heritage is a tool of political power, especially in conflict regions. Manipulation on platforms like Wikipedia can influence:
- Public perception
- International discourse
- Historical narratives
- Cultural identity

This project provides computational tools to document such interventions.

## Methodology
### Data Acquisition
- Wikimedia API
- Web scraping of article HTML and talk pages
- Metadata extraction

### Revision & Diff Analysis
- Successive revision comparison
- Framing and sentiment shifts
- Detection of ideological terminology

### Semantic Article Retrieval
Using multilingual embeddings (e.g., Alibaba-NLP/gte-multilingual).

### Narrative Analysis
LLM‑based annotations and topic modeling.

## Repository Structure
```
.
├── README.md
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   ├── XXX.ipynb
│   └── YYY.ipynb
├── src/
│   ├── processing/
│   ├── analysis/
│   └── utils/
├── requirements.txt
└── LICENSE
```
