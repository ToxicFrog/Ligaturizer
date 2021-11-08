FROM ubuntu:hirsute
WORKDIR /Ligaturizer

RUN apt-get update
RUN apt-get -y install make
RUN apt-get -y install python3-fontforge

COPY ligatures.py ligatures.py
COPY ligaturize.py ligaturize.py
COPY build.py build.py
COPY stat.py stat.py
COPY char_dict.py char_dict.py

COPY fonts/fira/distr/otf fonts/fira/distr/otf
COPY fonts/input fonts/input
COPY fonts/output fonts/output

COPY Makefile Makefile

ENTRYPOINT make
