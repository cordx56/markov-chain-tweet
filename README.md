# Markov Chain Tweet Generator

Run `$ docker build -t markovChainTweetGenerator .` and ``$ docker run -t --rm -v `pwd`/chainfiles:/script/chainfiles -p 5000:5000 markovChainTweetGenerator``

This program uses [jsvine/markovify](https://github.com/jsvine/markovify) and [MeCab](https://taku910.github.io/mecab/).  
To know all dependencies, see [Pipfile](Pipfile) and [Dockerfile](Dockerfile).
