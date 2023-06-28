FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install --no-install-recommends -qq -y \
    git \
    python3 \
    python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* 
#&& pip install mse-cli

RUN git clone https://github.com/Cosmian/mse-cli
WORKDIR /mse-cli
RUN pip install -r requirements.txt && pip install -U .

WORKDIR /mnt

ENTRYPOINT [ "mse", "home" ] 