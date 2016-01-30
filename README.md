To see a demo of rookie, go [here](http://54.213.128.229/?q=Mitch%20Landrieu/ "here"). This repo just holds the source code.

#### Rookie

Imagine you are a new reporter just assigned to a beat. Or a community activist interested in researching a certain political figure or government agency. News archives have lots of information that can help bring you up to speed. But reading the thousands (or millions) of news articles returned from a search enginge takes lots and lots of time. Rookie is designed to help. 

[Abe Handler](https://www.abehandler.com "Abe Handler") did most of the research and coding for Rookie. He got lots of conceptual help from [Steve Myers](https://twitter.com/myersnews "Steve Myers") and [Brendan O'Connor](http://brenocon.com "Brendan O'Connor").

This project began at [The Lens](http://www.thelensnola.org "The Lens") with [support](http://www.knightfoundation.org/grants/201550791/ "support") from the Knight foundation.

#### Tests and coverage

[![Build Status](https://travis-ci.org/AbeHandler/rookie.svg?branch=master)](https://travis-ci.org/AbeHandler/rookie) [![Coverage Status](https://coveralls.io/repos/AbeHandler/rookie/badge.svg?branch=master&service=github)](https://coveralls.io/github/AbeHandler/rookie?branch=master)

#### Indexing

1. Preprocessing: Rookie holds raw corpora in `corpora/[corpusname]/raw/all.extract`. It assumes that all.extract stores all.extract is a tsv with the pubdate in position 1, the text in position 5 and the headline in position 4. Like this: `NA\t1-1-2000\tNA\tNA\tHEADLINE\tTEXT`. An optional url goes in position 6.
2. Core NLP: Rookie processes corpora in `corpora/[corpusname]/raw/all.extract` by running them through @brenocon 's corenlp pipeline. Use `python getting_and_processing_corpora/corpus_proc.py --nlpjar path/to/corenlp --corpus corpusname`
3. Load to whoosh: `$ py getting_and_processing_corpora/load_to_whoosh.py --corpus [corpusname]`
4. Build sparse vectors for each doc. Store in Postgres: `$ py facets/build_sparse_matrix.py --corpus [corpusname]`

#### Code

`awsstuff` Code to load stuff into AWS (ec2 and s3)

`docker` The docker file and other docker stuff

`facets` the facet engine

`rookie_ui` React UI for rookie. use gulp b to push js to /webapp

`webapp` The Rookie webapp
