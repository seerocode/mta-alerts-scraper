FROM nickgryg/alpine-pandas:3.9
LABEL maintainer="roen@stanford.com"

RUN apk update

# Install system dependencies
RUN apk add tar gcc build-base xvfb 

# Selenium and BS4 dependencies
RUN apk add libxml2 libxml2-dev libxslt-dev firefox-esr py3-lxml

# Install geckodriver for Selenium
RUN rm  -rf /tmp/* /var/cache/apk/* && \
    wget https://github.com/mozilla/geckodriver/releases/download/v0.29.0/geckodriver-v0.29.0-linux64.tar.gz  && \
    tar -zvxf geckodriver-v0.29.0-linux64.tar.gz && \
    rm geckodriver-v0.29.0-linux64.tar.gz && \
    chmod a+x geckodriver && \
    mv geckodriver /usr/local/bin/

# Copy the dependencies to the container and install the python dependencies
RUN python3 -m pip install --upgrade pip
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install -r /tmp/requirements-docker.txt && rm /tmp/requirements-docker.txt

COPY . /app
WORKDIR /app

ENV PATH /app/bin:$PATH

ARG YEAR
ENV YEAR=$YEAR
RUN echo $YEAR

CMD ["sh", "-c", "python3 scraper.py $YEAR"]

