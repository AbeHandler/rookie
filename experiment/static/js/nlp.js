'use strict';

/* types of tokenization data structures

simple list of tokens
["hello","world","."]

tokens as offset/length pairs
{text: "hello world.", token_spans:[[0,5], [6,5], [11,1]]}
or [start,end) pairs
{text: "hello world.", token_spans:[[0,5], [6,7], [11,12]]}

in-token and out-of-token alternating representation. handy for UI rendering.
first item is OUT.  second is IN.  strict alternation.  last item could be either.
use a length representation, why not? like delta encoding.
{text: "hello world.", inout_lengths: [0,5,1,5,0,1]}
  len=0 OUT
  len=5 IN
  len=1 OUT
  len=5 IN
  len=0 OUT
  len=1 IN
then we're at total string length so stop.

rendering methods need some sort of all-contiguous-span representation,
at least so that whitespace and newlines get shown.

todo: write a method that aligns a list-of-strings against the text.
max-gap edit distance is the best way to do this
something hackier might also be possible


Final offset-aware tokenization object to return
{   text: "..string..",
    token_charspans: [[0,4], [7,10], ...],
    contig_lengths: [0,5,1,5,0,1, ...]
}
*/

// cat ../jsLDA/stoplist.txt | tr '\n' ' '
var STOPWORDS = "the and of for in a on is an this to by our that will have are with all must not more their has but can people new world from congress year which they these you years now than been who should its one make every other those them time was also there many great last first only would when most need own what because".trim().split(/\s+/);

function tokenize_and_clean(text) {
    // text: string
    let tok_strs=[], tok_charspans = [];  // token strings, token charspans
    let cur=0;
    let lens = tokenize_to_contiguous_lengths(text);
    let chars_with_token_start = {}, char_to_token_index={}, contigtok_to_realtok={};
    let contigtok_index=0;
    for (let len of lens) {
        let start=cur, end=cur+len;
        cur += len;
        // console.log("PROCESS '" +text.substr(start,end)+"'  " +start+" "+end);
        if (len==0) continue;
        let word = text.substr(start,len);
        word = word.toLowerCase().trim();

        let cti = contigtok_index;
        contigtok_index+=1; //for next loop

        if (word.length <= 0) continue;
        if (!word.match(/^[a-z0-9_-]+$/g)) continue;
        if (STOPWORDS.indexOf(word) != -1) continue;

        tok_strs.push(word);
        tok_charspans.push([start,end]);
        let realtok_index = tok_strs.length-1;
        // console.log(contigtok_index + " " + realtok_index);
        contigtok_to_realtok[cti] = realtok_index;
    }

    return {token_strings: tok_strs, token_charspans: tok_charspans, contig_lengths: lens,
        contigtok_to_realtok: contigtok_to_realtok,
    };
}

function tokenize_to_contiguous_lengths(str) {
    let split_re = /[^a-z0-9]+/gi;
    var match;
    var inout_lengths = [];
    var last=null;
    while (match = split_re.exec(str)) {
        if (last==null) {
            var len = match[0].length;
            if (match.index==0) {
                inout_lengths.push(len)
            } else if (match.index>0) {
                inout_lengths.push(0);
                inout_lengths.push(match.index);
                inout_lengths.push(len);
            } else { console.assert(false); }
            last = match.index + len;
        }
        else {
            var lastin_len = match.index - last;
            var out_len = match[0].length;
            inout_lengths.push(lastin_len);
            inout_lengths.push(out_len);
            last = match.index + out_len;
        }
    }
    if (last==null) last=0;
    if (last < str.length) {
        // end with an IN
        inout_lengths.push(str.length-last);
    }
    return inout_lengths;
}