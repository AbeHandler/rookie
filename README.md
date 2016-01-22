To see a demo of rookie, go [here](http://54.213.128.229/medviz?q=Mitch%20Landrieu/ "here"). This repo just holds the source code.

#### Rookie

Imagine you are a new reporter just assigned to a beat. Or a community activist interested in researching a certain political figure or government agency. News archives have lots of information that can help bring you up to speed. But reading the thousands (or millions) of news articles returned from a search enginge takes lots and lots of time. Rookie is designed to help. 

[Abe Handler](https://www.abehandler.com "Abe Handler") did most of the research and coding for Rookie. He got lots of conceptual help from [Steve Myers](https://twitter.com/myersnews "Steve Myers") and [Brendan O'Connor](http://brenocon.com "Brendan O'Connor").

This project began at [The Lens](http://www.thelensnola.org "The Lens") with [support](http://www.knightfoundation.org/grants/201550791/ "support") from the Knight foundation.

#### Tests and coverage

[![Build Status](https://travis-ci.org/AbeHandler/rookie.svg?branch=master)](https://travis-ci.org/AbeHandler/rookie) [![Coverage Status](https://coveralls.io/repos/AbeHandler/rookie/badge.svg?branch=master&service=github)](https://coveralls.io/github/AbeHandler/rookie?branch=master)

#### Indexing

Run the downloadandprocess to download from The Lens and run CoreNLP.

Run whooshy/loader.py to put the articles in the search engine.

#### Code

`aliaswork` Mostly old code trying to find captions for people using dependency graphs + AP style

`awsstuff` Code to load stuff into AWS (only ec2 right now). Note: Rookie used to run on AWS cloud search but now uses Whoosh. So some of that code is old.

`data` ~3500 articles from the Lens, plus NLP processing

`docker` The docker file and other docker stuff

`experiment` The main rookie app

`experiment/classes.py` SQL alchemy classes that wrap db tables

`experiment/builddb.py` loops over output from StanfordCoreNLP wrapper and adds to a postgres db

`experiment/snippet_maker.py` simple snippet maker that finds sentences that contain a query or facet as substring

`rookie_ui` React UI for rookie. use gulp b to push js to /webapp

`whooshy` Holds code for interacting with whoosh, the IR system for Rookie
