FROM centos:6.8
MAINTAINER support@filewave.com

ARG FILEWAVE_VERSION
ENV FILEWAVE_VERSION ${FILEWAVE_VERSION:-12.0.0}

ENV FILEWAVE_INSIDE_DOCKER_VERSION=${FILEWAVE_VERSION}

ENV LINUX_ZIPFILE_NAME=FileWave_Linux_${FILEWAVE_VERSION}.zip

ENV RPM_FW_SERVER=fwxserver-${FILEWAVE_VERSION}-1.0.x86_64

EXPOSE 19995 19996 20005 20006 20015 20016 20017 20030 20443 20445 20446

ENV INSTALL_DIR=/install
RUN mkdir -p "${INSTALL_DIR}"

COPY "${LINUX_ZIPFILE_NAME}" "${INSTALL_DIR}/"

RUN yum -y install unzip

WORKDIR "${INSTALL_DIR}"
RUN unzip -o "${LINUX_ZIPFILE_NAME}" && yum install -y --nogpgcheck "$RPM_FW_SERVER.rpm"

WORKDIR "/"
RUN rm -rf "${INSTALL_DIR}"

# stop the supervisord process ...
RUN /etc/init.d/fw-server stop

RUN mkdir -p /tmp/filewave

# Copy all the FW directories in the temporary space
RUN cp -r /fwxserver/DB \
    /fwxserver/"Data Folder" \
    /usr/local/filewave/certs \
    /usr/local/filewave/fwcld \
    /usr/local/filewave/apache/conf \
    /tmp/filewave/

RUN cp -r /usr/local/filewave/postgresql/conf \
    /tmp/filewave/postgres_conf

# NOTE: grouping directories reduces the number of layers in the final image (a good thing)
VOLUME [ "/fwxserver/DB", "/fwxserver/Data Folder", "/usr/local/filewave/postgresql/conf", "/usr/local/filewave/apache/conf", "/usr/local/filewave/apache/logs", "/usr/local/filewave/apache/passwords", "/usr/local/filewave/certs", "/usr/local/filewave/fwcld",  "/usr/local/filewave/ipa", "/usr/local/filewave/log", "/usr/local/filewave/media", "/usr/local/filewave/tmp/"]

COPY ./docker-entrypoint.sh /
# overwrite the supervisord configuration to not use core dumps:
COPY supervisord-server-docker-full.conf /usr/local/etc/filewave/supervisor/supervisord-server-full.conf

ENTRYPOINT [ "/docker-entrypoint.sh" ]