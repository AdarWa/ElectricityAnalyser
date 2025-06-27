FROM python:3-alpine

RUN apk add --virtual .build-dependencies \
            --no-cache \
            python3-dev \
            build-base \
            linux-headers \
            pcre-dev

RUN apk add --no-cache pcre

RUN mkdir -p /config

WORKDIR /app
COPY /app /app
COPY /app/config.yaml /config/config.yaml
COPY /app/wsgi.ini /app/wsgi.ini

RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt
RUN pip install uwsgi

RUN apk del .build-dependencies && rm -rf /var/cache/apk/*

EXPOSE 5000
CMD ["uwsgi", "--ini", "/app/wsgi.ini"]