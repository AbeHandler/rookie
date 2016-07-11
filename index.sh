#!/bin/bash
# This script builds all of the indexes rookie needs: whoosh, the meta data file and the db

python getting_and_processing_corpora/corpus_proc.py --nlpjar ~/research/nytweddings/stanford-corenlp-full-2015-04-20/ --corpus lens
python getting_and_processing_corpora/corpus_proc.py --nlpjar ~/research/nytweddings/stanford-corenlp-full-2015-04-20/ --corpus gawk
py getting_and_processing_corpora/fill_min_max_pubdates.py --corpus lens --min 1/1/2010 --max 4/1/2015
py getting_and_processing_corpora/fill_min_max_pubdates.py --corpus gawk --min 10/1/2002 --max 4/20/2012
py getting_and_processing_corpora/fill_min_max_pubdates.py --corpus election --min 1/1/2016 --max 12/31/2016
python getting_and_processing_corpora/load_to_whoosh.py --corpus lens
python getting_and_processing_corpora/load_to_whoosh.py --corpus gawk
python facets/build_sparse_matrix.py --corpus lens
python facets/build_sparse_matrix.py --corpus gawk
