FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y \
        locales

RUN sed -i '/ja_JP.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8

COPY booker /usr/src/booker

WORKDIR /usr/src
COPY setup.py .
RUN pip install .

ENV PATH /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/chrome
