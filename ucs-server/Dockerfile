FROM centos:6.6
MAINTAINER support@filewave.com

ARG FILEWAVE_VERSION
ENV FILEWAVE_VERSION ${FILEWAVE_VERSION:-11.2.2}

ENV LINUX_ZIPFILE_NAME=FileWave_Linux_${FILEWAVE_VERSION}.zip

ENV RPM_MDM_SERVER=fw-mdm-server-${FILEWAVE_VERSION}-1.0.x86_64
ENV RPM_FW_SERVER=fwxserver-${FILEWAVE_VERSION}-1.0.x86_64

EXPOSE 2195 5223 9432 19995 19996 20005 20006 20015 20016 20017 20030 20443 20445 20446

ENV INSTALL_DIR=/install
RUN mkdir -p "${INSTALL_DIR}"

COPY "${LINUX_ZIPFILE_NAME}" "${INSTALL_DIR}/"

RUN yum -y install unzip

RUN cd /install && unzip -o "${LINUX_ZIPFILE_NAME}" && yum install -y --nogpgcheck "$RPM_FW_SERVER.rpm" \
  && cd / && rm -rf /install/*

COPY docker-entrypoint.sh ${INSTALL_DIR}/docker-entrypoint.sh

# stop the supervisord process ...
RUN /etc/init.d/fw-server stop

# NOTE: /fwxserver/DB/pg_data is NOT exposed as a volume as the current design calls for the data
# to be present within the container, only on export/import is it leaving the confines of its docker container.
VOLUME [ "/fwxserver", "/fwxserver/Data Folder" ]

VOLUME [ "/usr/local/filewave/apache/conf", "/usr/local/filewave/apache/logs", "/usr/local/filewave/apache/passwords" ]
VOLUME [ "/usr/local/filewave/certs", "/usr/local/filewave/fwcld", "/usr/local/filewave/django" ]

VOLUME [ "/usr/local/filewave/ipa", "/usr/local/filewave/log", "/usr/local/filewave/media", "/usr/local/filewave/postgresql/conf" ]
VOLUME [ "/usr/local/filewave/postgresql/log", "/usr/local/filewave/tmp", "/usr/local/filewave/scripts" ]

CMD [ "/usr/local/filewave/python.v27/bin/supervisord", "-n", "-c", "/usr/local/etc/filewave/supervisor/supervisord-server.conf" ]

