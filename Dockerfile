FROM ceph/ceph:v15

RUN mkdir /rbd-prober

WORKDIR /rbd-prober

ADD requirements.txt .
RUN pip3 install -r requirements.txt

ADD . .

ENV LOGURU_LEVEL INFO

EXPOSE 8000

ENTRYPOINT [ "gunicorn", "-b", "0.0.0.0:8000", "main:app_dispatch", "--access-logfile", "-", "--error-logfile", "-" ]
