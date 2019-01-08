ARG BASE_IMAGE
FROM $BASE_IMAGE

# Set default locale.
ENV LANG C.UTF-8

RUN pip3 install Flask==1.0.2
RUN pip3 install gunicorn==19.9.0

# Install surround to base image
COPY . /opt/surround/
ENV VERSION_TAG=1.0.0
WORKDIR /opt/surround/
RUN python3 setup.py install

# Clean up to reduce image size.
RUN rm -rf /root/.cache/pip /var/lib/apt/lists/*
