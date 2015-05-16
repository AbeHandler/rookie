rm *html
rm files/*
rm out.txt
touch out.txt

#curl for each summary page
for i in {1..413}
do
   curl -o "$i"".html" "http://thelensnola.org/page/$i/?s="
done

#get the urls
python articles_getter_prep.py

k=1
while read line; do
    fn=$(echo $line | cut -d "/" -f 4,5,6,7 | tr "/" "_")
    echo "$line"
    curl $line -o "files/""$fn"".txt"
    echo $line
    ((k++))
    echo "$k"
done < out.txt

rm files/corrections_.txt

rm files/argolinkroundups* #we dont want these

python preprocessor.py