rm keys.csv.gz
python rookie/scripts/counter.py
python rookie/scripts/pmi_calculator.py
gzip keys.csv
find data/pmis -name '*json'  -exec gzip "{}" \;
./deployapp.sh
