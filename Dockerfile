# FROM alpine:3.12
FROM nickgryg/alpine-pandas:3.9
LABEL maintainer="roen@stanford.com"

RUN apk update

# Install system dependencies
RUN apk --no-cache add tar gcc build-base xvfb

# Python dependencies
# RUN apk add python3 python3-dev py3-pip 

# Selenium and BS4 dependencies
RUN apk  --no-cache add libxml2 libxml2-dev libxslt-dev firefox-esr py3-lxml

# RUN apk add chromium chromium-chromedriver

# ENV CHROME_BIN=/usr/bin/chromium-browser \
#     CHROME_PATH=/usr/lib/chromium/


RUN rm  -rf /tmp/* /var/cache/apk/* && \
    wget https://github.com/mozilla/geckodriver/releases/download/v0.29.0/geckodriver-v0.29.0-linux64.tar.gz  && \
    tar -zvxf geckodriver-v0.29.0-linux64.tar.gz && \
    rm geckodriver-v0.29.0-linux64.tar.gz && \
    chmod a+x geckodriver && \
    mv geckodriver /usr/local/bin/

# RUN export PATH=$PATH:/usr/bin/geckodriver.exe
# RUN geckodriver --version

# Copy the dependencies to the container and install the python dependencies
RUN python3 -m pip install --upgrade pip
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

COPY . /app
WORKDIR /app

ENV PATH /app/bin:$PATH

ARG YEAR
ENV YEAR=$YEAR
RUN echo $YEAR

CMD ["sh", "-c", "python3 scraper.py $YEAR"]
# CMD ["python3", "./scraper.py ${year}"]
# ENTRYPOINT [ "start.sh" ]

