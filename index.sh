#!/bin/bash
# This script builds all of the indexes rookie needs: whoosh, the meta data file and the db

python getting_and_processing_corpora/corpus_proc.py --nlpjar ~/research/nytweddings/stanford-corenlp-full-2015-04-20/ --corpus lens
dropdb 'rookie' --if-exists
createdb -O rookie rookie
python webapp/classes.py
python getting_and_processing_corpora/load_to_whoosh.py --corpus lens
python facets/build_matrix.py --corpus lens
