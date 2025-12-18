# Monita-privata: Computational Analysis of the Monita privata/secreta Editions Dataset

## Introduction

This repository contains the code used for the **computational processing, cleaning, and analysis** of the bibliographic dataset related to the historical polemic **Monita privata** (later referred to also as *Monita secreta*). This unique anti-Jesuit polemic emerged in early seventeenth-century Europe, likely composed between 1606 and 1612. The text gained notoriety as an ostensible covert guide for Jesuit members on wielding influence, wealth, and power through subversive means. The analysis here reveals the impact of the *Monita* in catalyzing anti-Jesuit sentiment and fueling conspiracy theories about Jesuit secrecy and manipulation across Europe and the Americas.

## Data Source

The data utilized by the scripts in this repository is sourced from an expansive, scholarly resource published on Zenodo.

| Metric | Details |
| :--- | :--- |
| **Dataset Title** | Database of the Monita privata (secreta) editions/reprints/translations |
| **DOI Zenodo** | [10.5281/zenodo.14049942](https://doi.org/10.5281/zenodo.14049942) |
| **Data Format** | Terse RDF Triple Language (TTL) with attached metadata and identifiers |
| **License** | Creative Commons Attribution 4.0 International (CC BY 4.0) |
| **Creators** | Robert A. Maryks (Data collector), Cezary Rosiński (Data curator), Michał E. Nowakowski (Data collector) |

**Key Dataset Focus:**

The dataset systematically enriches bibliographic information with geographical identifiers and temporal references to provide clarity on the publication history. It challenges the traditional attribution of authorship to the ex-Jesuit Hieronim Zahorowski (d.1634). The resource posits that the *Monita* may have been a **Venetian (-inspired) fabrication**. This dataset includes key fields such as Title, Year of Publication (estimated or range), Place of Publication (Geonames identifier), and additional research-oriented metadata like `monita:placeInText`, `monita:placeType`, `monita:privataInTitle`, `monita:secretaInTitle`, and `monita:yearCertainty`.

The data was collected from extensive archival and library exploration in various cities, including Cracow, Vilnius, Rome, Lublin, Warsaw, and Berlin.

## Repository Structure and Functionality

The GitHub repository contains Python scripts (0.3%) and Jupyter Notebooks (38.5%), indicating a focus on data processing and computational analysis of the dataset.

```
.
├── data/                                      # Directory for processed and input data files.
├── __pycache__/                               # Python cache files.
├── .gitignore                                 # Git ignore file.
├── jojs_cleaningpy.py                         # Script dedicated to cleaning and preparing data.
├── journal_of_jesuit_studies_web_scraping.py  # Script for gathering supplemental data from external web sources.
├── monita_privata_main.py                     # Principal script for processing the core Monita privata dataset.
├── monita_privata_e-enlightenment.py          # Script likely used for contextual analysis against e-enlightenment data.
├── monita_privata_places.py                   # Script focused on processing and analyzing geographical data (Geonames identifiers).
├── jesuit_studies.ipynb                       # Jupyter Notebook for interactive data exploration.
├── ph_topic_modelling.py                      # Topic Modelling script for extracting themes.
├── topic_model2.py                            # Variant of the Topic Modelling script.
└── topic_modeling.py                          # General script implementation for Topic Modelling.
```

**Computational Applications:**

*   **Topic Modelling:** Utilizing scripts (e.g., `topic_modeling.py`, `ph_topic_modelling.py`) to analyze and categorize dominant themes and narratives within the bibliographic and contextual metadata.
*   **Geographical Analysis:** Processing the Geonames identifiers to map and visualize the dissemination of the *Monita privata* editions across different regions over time.
*   **Data Preparation:** Cleaning and transforming the Terse RDF Triple Language (TTL) data for further quantitative study.

## Usage and Funding

The inclusion of regional identifiers and contextual data supports a nuanced analysis, making this resource invaluable for understanding the geographic and political dimensions of early modern anti-Jesuit subversive and parodic literature.

The dataset has been used in the project **“Literatura antyjezuicka w Rzeczypospolitej Obojga Narodów”** [Anti-Jesuit literature in the Polish-Lithuanian Commonwealth]. This research project was funded by the Polish National Science Centre (NCN).
