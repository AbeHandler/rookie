#from root run...
python rookie/downloadandprocess/lensdownloader.py
py rookie/downloadandprocess/get_url_list.py > allurls.txt
cat allurls.txt | parallel -j20 --eta 'python rookie/downloadandprocess/lensprocessor.py {} {#}'
python rookie/scripts/counter.py # find the counts and joint counts
python rookie/scripts/counter2.py # find the pmis