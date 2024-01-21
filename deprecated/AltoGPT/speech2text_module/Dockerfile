# didn't use anymore since we can't connect mic to the docker container yet

FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt upgrade -y && \
    apt install -y build-essential ffmpeg vim curl python3 python3-pip portaudio19-dev python3-pyaudio && \
    python3 -m pip install --upgrade pip
