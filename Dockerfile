FROM ceph/ceph:v15

RUN mkdir /rbd-prober

WORKDIR /rbd-prober

ADD requirements.txt .
RUN pip3 install -r requirements.txt

ADD . .

ENV LOGURU_LEVEL INFO

EXPOSE 8000

ENTRYPOINT [ "gunicorn", "--chdir", "rbd_prober", "app:app_dispatch" ]
