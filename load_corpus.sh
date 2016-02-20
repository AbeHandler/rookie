#! /bin/bash
mkdir -p corpora/$1/processed
python getting_and_processing_corpora/corpus_proc.py --nlpjar ~/research/nytweddings/stanford-corenlp-full-2015-04-20/ --corpus $1
py getting_and_processing_corpora/add_to_db.py --corpus $1