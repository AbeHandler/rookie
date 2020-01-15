![alt text](screenshot.png "Rookiew")


#### Rookie

Imagine you are a new reporter just assigned to a beat. Or a community activist interested in researching a certain political figure or government agency. News archives have lots of information that can help bring you up to speed. But reading the thousands (or millions) of news articles returned from a search enginge takes lots and lots of time. Rookie is designed to help. 

[Abe Handler](https://www.abehandler.com "Abe Handler") did most of the research and coding for Rookie. He got lots of conceptual help from [Steve Myers](https://twitter.com/myersnews "Steve Myers") and [Brendan O'Connor](http://brenocon.com "Brendan O'Connor").

This project began at [The Lens](http://www.thelensnola.org "The Lens") with [support](http://www.knightfoundation.org/grants/201550791/ "support") from the Knight foundation.

#### Code

You will need a copy of [Brendan O'Connor's wrapper for StanfordCore NLP](https://github.com/brendano/stanford_corenlp_pywrapper) to index Rookie documents.

`facets` the facet engine

`rookie_ui` React UI for rookie. use gulp b to push js to /webapp

`webapp` The Rookie webapp

#### Import new corpora

To import a new corpus you need to have a user=rookie and database=rookie on a local postgres install w/ default ports. 

You will need a file: `corpora/[corpus]/raw/all.extract` which is a tsv, where [corpus] is a corpus name like   h`haiti`.

The format of the tsv is indexed at 0. 
- Field 1 should be the publication date in the format `YYYYMMDD_0000000` where the 0s dont matter. 
- Field 4 should be the headline. 
- Field 5 should be the raw document text.

Then run `getting_and_processing_corpora/load_corpus.sh [corpus]`. The import process requires python2 and a bunch of old dependencies specified in requirements.txt. At some point this might be updated, maybe.

#### Changes

- 8/3/16: Add in all sentences scrolling after user study. Change back to linear scaling. More event-y. See issue.
- 8/4/16: Suggestion from reporter 8/3/16, show headline tooltips
- 8/17/16: change ranking of snippets in snippet box. QF go higher. Then Q or F. Before was chron order. Easier to see QF relationship
- 8/19/16: hash to eliminate randomness in picking docs. add pagination in snippets box to allow flipping thru docs.

