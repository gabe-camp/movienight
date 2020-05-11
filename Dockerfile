FROM arm32v7/python:3.6-alpine

MAINTAINER Gabriel Campanella "gabe.camp@gmail.com"

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r /app/requirements.txt

COPY . /app

# removed because will be specified via k8s
#
#ENTRYPOINT [ "python" ]
#
#CMD [ "app.py" ]
