FROM quay.io/ceph/ceph:v16.2.9

ENV PYTHONUNBUFFERED 1

RUN mkdir /rbd-prober

WORKDIR /rbd-prober

ADD requirements.txt .
RUN pip3 install -r requirements.txt

ADD . .

EXPOSE 8000

ENTRYPOINT [ "python3", "app.py" ]
