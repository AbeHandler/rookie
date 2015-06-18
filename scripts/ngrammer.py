import nltk
import glob
import json
from rookie.datamanagement.lensconsolidator import get_full_text


files = glob.glob("/Volumes/USB/lens_processed/*")


def get_grams(text):
    unigrams = text.split(" ")
    bigrams = nltk.bigrams(unigrams)
    trigrams = nltk.trigrams(unigrams)
    return (unigrams, bigrams, trigrams)


for f in files:
    try:
        with open(f, "r") as data_file:
            data = json.load(data_file)
            full_text = get_full_text(data)
            grams = get_grams(full_text)
            print grams
    except ValueError:
        pass
