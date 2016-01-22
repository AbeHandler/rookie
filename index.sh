#!/bin/bash
# This script builds all of the indexes rookie needs: whoosh, the meta data file and the db

python whooshy/loader.py
python facets/build_matrix.py
python experiment/builddb.py