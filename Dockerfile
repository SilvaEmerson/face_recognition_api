FROM python:3.5-slim

RUN apt-get -y update
RUN apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-dev \
    libavcodec-dev \
    libavformat-dev \
    libboost-all-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    software-properties-common \
    zip \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

COPY ./dlib-19.8 /root/dlib

RUN cd  /root/dlib/ && \
    python3 setup.py install --yes USE_AVX_INSTRUCTIONS

COPY ./face_recognition /root/face_recognition

RUN cd /root/face_recognition && \
     pip3 install -r requirements.txt

CMD ["python3", "./root/face_recognition/API.py"]
