python getting_and_processing_corpora/countrymaker.py -country indonesia
python getting_and_processing_corpora/countrymaker.py -country cuba
python getting_and_processing_corpora/countrymaker.py -country slovenia
python getting_and_processing_corpora/countrymaker.py -country malaysia
python getting_and_processing_corpora/countrymaker.py -country philippines
python getting_and_processing_corpora/countrymaker.py -country estonia
python getting_and_processing_corpora/countrymaker.py -country singapore
python getting_and_processing_corpora/countrymaker.py -country rwanda
python getting_and_processing_corpora/countrymaker.py -country haiti
python getting_and_processing_corpora/countrymaker.py -country colombia



# countries. change to param at some point
python getting_and_processing_corpora/load_to_whoosh.py --corpus indonesia
python getting_and_processing_corpora/load_to_whoosh.py --corpus cuba
python getting_and_processing_corpora/load_to_whoosh.py --corpus slovenia
python getting_and_processing_corpora/load_to_whoosh.py --corpus malaysia
python getting_and_processing_corpora/load_to_whoosh.py --corpus philippines
python getting_and_processing_corpora/load_to_whoosh.py --corpus estonia
python getting_and_processing_corpora/load_to_whoosh.py --corpus singapore
python getting_and_processing_corpora/load_to_whoosh.py --corpus rwanda
python getting_and_processing_corpora/load_to_whoosh.py --corpus haiti
python getting_and_processing_corpora/load_to_whoosh.py --corpus colombia

py getting_and_processing_corpora/fill_min_max_pubdates.py --corpus indonesia --min 1/1/1987 --max 12/1/2007
py getting_and_processing_corpora/fill_min_max_pubdates.py --corpus cuba --min 1/1/1987 --max 12/1/2007
py getting_and_processing_corpora/fill_min_max_pubdates.py --corpus slovenia --min 1/1/1987 --max 12/1/2007
py getting_and_processing_corpora/fill_min_max_pubdates.py --corpus malaysia --min 1/1/1987 --max 12/1/2007
py getting_and_processing_corpora/fill_min_max_pubdates.py --corpus philippines --min 1/1/1987 --max 12/1/2007
py getting_and_processing_corpora/fill_min_max_pubdates.py --corpus estonia --min 1/1/1987 --max 12/1/2007
py getting_and_processing_corpora/fill_min_max_pubdates.py --corpus singapore --min 1/1/1987 --max 12/1/2007
py getting_and_processing_corpora/fill_min_max_pubdates.py --corpus rwanda --min 1/1/1987 --max 12/1/2007
py getting_and_processing_corpora/fill_min_max_pubdates.py --corpus haiti --min 1/1/1987 --max 12/1/2007
py getting_and_processing_corpora/fill_min_max_pubdates.py --corpus colombia --min 1/1/1987 --max 12/1/2007

python facets/build_sparse_matrix.py --corpus indonesia
python facets/build_sparse_matrix.py --corpus cuba
python facets/build_sparse_matrix.py --corpus slovenia
python facets/build_sparse_matrix.py --corpus malaysia
python facets/build_sparse_matrix.py --corpus philippines
python facets/build_sparse_matrix.py --corpus estonia
python facets/build_sparse_matrix.py --corpus singapore
python facets/build_sparse_matrix.py --corpus rwanda
python facets/build_sparse_matrix.py --corpus haiti
python facets/build_sparse_matrix.py --corpus colombia
