FROM ubuntu:latest
RUN mkdir /app
COPY . /app
WORKDIR /app

RUN apt-get update && \
    apt-get install -y python3.10

RUN apt-get update && \
    apt-get install -y python3-pip && \
    pip3 install --upgrade pip && \
    pip3 install -r /app/requirements.txt

CMD ["python3", "-u", "recbot.py"]