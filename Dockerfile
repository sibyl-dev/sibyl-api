FROM python:3.6-stretch

RUN apt-get update

ADD . /sibylapp
WORKDIR /sibylapp
RUN cd sibyl && python -m pip install --upgrade pip && pip install -e .[dev]
RUN cd ..
RUN pip install -e .[dev]

