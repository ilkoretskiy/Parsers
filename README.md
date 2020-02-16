# PARSERA
An example how you can use selenium + beautiful soup for parsing websites. Quora and https://www.akusherstvo.ru/ selected for educational purpose only.


# Why
I made this project for training in parsing and out of curiosity. You won't find unittests here, good exception handling nor good documentation. However it could be useful for reuse for somebody. For example in akusherstvo you could find an example how to work with cookies in python. Also how to parse dynamically generated content like in quora.

# How it works
## Quora
A script that do all the work is *question_parser.py*. There you'll find a line with reading of "result.json" file. It is expected in this file will be a list of links to quora questions. 

