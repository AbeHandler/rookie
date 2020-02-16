#! /bin/bash

rm -rf corpora/$1/processed
rm -rf indexes/$1

mkdir -p indexes/$1
mkdir -p corpora/$1/processed

python getting_and_processing_corpora/corpus_proc.py --corpus $1

## this just tells the db that you have a corpus called "haiti" or "syria" for instance

#python getting_and_processing_corpora/add_to_db.py --corpus $1
python getting_and_processing_corpora/add_to_file_sys.py --corpus haiti

### loading the corpus to whoosh. I think this also makes the ngram index.

python getting_and_processing_corpora/build_indexes_and_load_docs_to_db.py --corpus $1

#python getting_and_processing_corpora/fill_min_max_pubdates.py --corpus $1

python facets/build_sparse_matrix.py --corpus $1