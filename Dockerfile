FROM tiangolo/uwsgi-nginx:python3.6-alpine3.7

COPY requirements.txt /simpleshop/
COPY project /simpleshop/project
COPY migrations /simpleshop/migrations
COPY setup.py /simpleshop/
COPY setup.cfg /simpleshop/

RUN apk update \
  && apk add --no-cache --virtual build-deps gcc python3-dev musl-dev \
  && apk add postgresql-dev \
  && pip3 install --upgrade pip \
  && pip3 install --trusted-host pypi.python.org -r /simpleshop/requirements.txt \
  && pip3 install -e /simpleshop \
  && apk del build-deps

ENV NGINX_WORKER_PROCESSES auto
ENV UWSGI_INI /simpleshop/project/uwsgi.ini

WORKDIR /simpleshop

COPY docker/start.sh /

CMD ["/start.sh"]