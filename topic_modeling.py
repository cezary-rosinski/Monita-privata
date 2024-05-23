from tqdm import tqdm
from bs4 import BeautifulSoup
import sys
sys.path.insert(1, 'C:/Users/Cezary/Documents/IBL-PAN-Python')
from my_functions import gsheet_to_df
import pickle
import Levenshtein as lev
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor
import os
from glob import glob
import regex as re
from copy import deepcopy
from PyPDF2 import PdfReader
from PyPDF2.errors import DependencyError, EmptyFileError, PdfReadError

#%%
#pdf to txt
path = r"C:\Users\Cezary\Documents\Monita-privata\data\konferencja poznań\pdf/"
pdf_files = [f for f in glob(f"{path}*", recursive=True)]

for pdf_file in tqdm(pdf_files):
    text_title = pdf_file.split('\\')[-1].split('.')[0]
    reader = PdfReader(pdf_file)
    extracted_text = '/n'.join([e.extract_text() for e in reader.pages])
    with open(f'data/konferencja poznań/txt/{text_title}.txt', 'wt', encoding='utf-8') as f:
        f.write(extracted_text)
#usunąć download information


#%%
import os
import spacy 
from spacy import displacy
import gensim
from gensim.corpora import Dictionary
from gensim.models import LdaModel, CoherenceModel, LsiModel, HdpModel
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
stop_words = list(stopwords.words('english'))
from spacy.tokens import Doc
from gensim import corpora

path = r"C:\Users\Cezary\Documents\Monita-privata\data\konferencja poznań\txt/"
txt_files = [f for f in glob(f"{path}*", recursive=True)]

txt_dict = {}
for txt_file in tqdm(txt_files):
    text_key = txt_file.split('\\')[-1].split('.')[0]
    with open(txt_file, 'rt', encoding='utf-8') as f:
        text_value = f.read()
    txt_dict.update({text_key: text_value})

nlp = spacy.load('en_core_web_sm')

def preprocess(texts):
    processed_texts = []
    for doc in nlp.pipe(texts, disable=["parser", "ner"]):
        # Tokenize, remove stopwords and non-alphabetic tokens, and lemmatize
        tokens = [token.lemma_ for token in doc if token.is_alpha and token.text.lower() not in stop_words]
        processed_texts.append(tokens)
    return processed_texts

texts = list(txt_dict.values())

processed_texts = preprocess(texts)

# Create a dictionary representation of the documents
dictionary = corpora.Dictionary(processed_texts)

# Filter out extreme values from the dictionary (optional)
dictionary.filter_extremes(no_below=5, no_above=0.5)

# Create a corpus: list of bag-of-words representation of the documents
corpus = [dictionary.doc2bow(text) for text in processed_texts]

from gensim.models import LdaModel

# Set parameters for the LDA model
num_topics = 8  # Define the number of topics

# Build the LDA model
lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15)

# Print the topics
for idx, topic in lda_model.print_topics(-1):
    print(f"Topic: {idx}\nWords: {topic}\n")

from gensim.models.coherencemodel import CoherenceModel

# Compute Coherence Score
coherence_model_lda = CoherenceModel(model=lda_model, texts=processed_texts, dictionary=dictionary, coherence='c_v')
coherence_lda = coherence_model_lda.get_coherence()
print(f'Coherence Score: {coherence_lda}')













for stopword in stop_words:
    lexeme = nlp.vocab[stopword]
    lexeme.is_stop = True
    
docs = list(nlp.pipe(list(txt_dict.values())))
c_doc = Doc.from_docs(docs)

bigram = gensim.models.phrases.Phrases(c_doc)
texts = [bigram[line] for line in texts]
texts = [bigram[line] for line in texts]
print(texts[0])









