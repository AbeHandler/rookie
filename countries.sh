#!/usr/bin/env bash
declare -a countries=("cuba", "haiti")

./remake_db.sh # if you dont do this before indexing stuff gets messed up

for i in "${countries[@]}"
do
   echo "$i"
   python getting_and_processing_corpora/countrymaker.py -country "$i"
   # sort corpora/"$i"/processed/all.anno_plus | uniq > t && mv t corpora/"$i"/processed/all.anno_plus
   python getting_and_processing_corpora/load_to_whoosh.py --corpus "$i"
   python getting_and_processing_corpora/fill_min_max_pubdates.py --corpus "$i" --min 1/1/1987 --max 12/1/2007
   python facets/build_sparse_matrix.py --corpus "$i"
done
