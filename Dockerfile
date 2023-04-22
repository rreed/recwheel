FROM ubuntu:latest

RUN apt-get update
RUN apt-get install -y python3.10 python3-pip
RUN pip3 install --upgrade pip

RUN mkdir /app
COPY . /app
WORKDIR /app

RUN pip3 install -r /app/requirements.txt

RUN mkdir /data

CMD ["python3", "-u", "recbot.py"]
