FROM centos:6.6
MAINTAINER support@filewave.com

ARG FILEWAVE_VERSION
ENV FILEWAVE_VERSION ${FILEWAVE_VERSION:-12.0.0}

ENV LINUX_ZIPFILE_NAME=FileWave_Linux_${FILEWAVE_VERSION}.zip

ENV RPM_FW_SERVER=fwxserver-${FILEWAVE_VERSION}-1.0.x86_64

EXPOSE 2195 5223 9432 19995 19996 20005 20006 20015 20016 20017 20030 20443 20445 20446

ENV INSTALL_DIR=/install
RUN mkdir -p "${INSTALL_DIR}"

COPY "${LINUX_ZIPFILE_NAME}" "${INSTALL_DIR}/"

RUN yum -y install unzip

WORKDIR "${INSTALL_DIR}"
RUN unzip -o "${LINUX_ZIPFILE_NAME}" && yum install -y --nogpgcheck "$RPM_FW_SERVER.rpm"

# extract pre/post install/uninstall scripts
# TODO

# stop the supervisord process ...
RUN /etc/init.d/fw-server stop

# Copy all the FW directories in the temporary space
RUN cp -r /fwxserver/DB \
    /fwxserver/"Data Folder" \
    /usr/local/filewave/certs \
    /usr/local/filewave/apache/conf \
    /usr/local/filewave/tmp/

# NOTE: grouping directories reduces the number of layers in the final image (a good thing)
VOLUME [ "/fwxserver/DB", "/fwxserver/Data Folder", "/usr/local/filewave/apache/conf", "/usr/local/filewave/apache/logs", "/usr/local/filewave/apache/passwords", "/usr/local/filewave/certs", "/usr/local/filewave/fwcld",  "/usr/local/filewave/ipa", "/usr/local/filewave/log", "/usr/local/filewave/media"]

COPY ./docker-entrypoint.sh /

ENTRYPOINT [ "/docker-entrypoint.sh" ]