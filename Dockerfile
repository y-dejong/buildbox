FROM fedora:latest
ENV HOME /root
RUN dnf group install -y --with-optional \
"Development Tools" \
"C Development Tools and Libraries"

RUN mkdir /root/workspace
WORKDIR /root/workspace

SHELL ["/bin/bash", "-c"]
