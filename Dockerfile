FROM arm32v7/python:3.6-alpine

MAINTAINER Gabriel Campanella "gabe.camp@gmail.com"

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r /app/requirements.txt

COPY . /app

EXPOSE 8080
CMD [ "python", "app.py" ]
