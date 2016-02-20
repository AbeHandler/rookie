python getting_and_processing_corpora/corpus_proc.py --nlpjar /Users/ahandler/research/nytweddings/stanford-corenlp-full-2015-04-20 --corpus iphone
python getting_and_processing_corpora/load_to_whoosh.py --corpus iphone
python facets/build_sparse_matrix.py --corpus iphone