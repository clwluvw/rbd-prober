FROM ceph/ceph:v15

RUN mkdir /rbd-prober

WORKDIR /rbd-prober

ADD requirements.txt .
RUN pip3 install -r requirements.txt

ADD . .

EXPOSE 8000

ENTRYPOINT [ "python3", "main.py" ]
