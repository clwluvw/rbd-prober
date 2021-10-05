FROM ceph/ceph:v16.2.5

RUN mkdir /rbd-prober

WORKDIR /rbd-prober

ADD requirements.txt .
RUN pip3 install -r requirements.txt

ADD . .

ENV LOGURU_LEVEL INFO

EXPOSE 8000

ENTRYPOINT [ "python3", "app.py" ]
