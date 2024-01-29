FROM python:3.9

COPY . . 

COPY ./requirements.txt requirements.txt
COPY ./startup.sh startup.sh

#chromium has lots of dependencies, this was the easiest way to install them all. But chromium itself is supplied via pip.
RUN apt-get -y update && apt-get -y install chromium-driver firefox-esr && \
dpkg --remove chromium chromium-driver chromium-common chromium-sandbox

RUN apt-get -y install tightvncserver x11-apps jwm expect pwgen

RUN pip install -e .

RUN pip install --no-cache-dir --upgrade -r requirements.txt
