import json
import glob


TO_PROCESS = glob.glob('/Volumes/USB/lens_processed/*')


def get_grams(text):
    unigrams = text.split(" ")
    bigrams = nltk.bigrams(unigrams)
    trigrams = nltk.trigrams(unigrams)
    return (unigrams, bigrams, trigrams)


def get_full_text(data):
    sentences = data['entities']['sentences']
    full_text = ""
    for sentence in sentences:
        full_text = full_text + sentence['lemmas']
    return full_text


for process_file in TO_PROCESS:
    try:
        output = {}
        with open(process_file, 'r') as processed:
            data = json.load(processed)
            print full_text
    except ValueError:
        print 'value error'
    except TypeError:
        print 'type error'
