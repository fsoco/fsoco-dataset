# ubuntu 20.04
FROM ubuntu:focal

WORKDIR /app
COPY ./tools/docker/scripts /app/

RUN bash /app/install_apt_packages.sh

ARG user=fsoco
RUN useradd -ms /bin/bash ${user}
USER fsoco

WORKDIR /home/fsoco/app
COPY ./tools .

RUN bash /app/install_fsoco.sh

RUN cp /app/entrypoint.sh .
RUN chmod 700 entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ]
