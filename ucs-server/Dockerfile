FROM centos:6.6
MAINTAINER support@filewave.com

ARG FILEWAVE_VERSION
ENV FILEWAVE_VERSION ${FILEWAVE_VERSION:-11.2.3}

ENV LINUX_ZIPFILE_NAME=FileWave_Linux_${FILEWAVE_VERSION}.zip

ENV RPM_MDM_SERVER=fw-mdm-server-${FILEWAVE_VERSION}-1.0.x86_64
ENV RPM_FW_SERVER=fwxserver-${FILEWAVE_VERSION}-1.0.x86_64

EXPOSE 2195 5223 9432 19995 19996 20005 20006 20015 20016 20017 20030 20443 20445 20446

ENV INSTALL_DIR=/install
RUN mkdir -p "${INSTALL_DIR}"

COPY "${LINUX_ZIPFILE_NAME}" "${INSTALL_DIR}/"

RUN yum -y install unzip

WORKDIR "${INSTALL_DIR}"
RUN unzip -o "${LINUX_ZIPFILE_NAME}" && yum install -y --nogpgcheck "$RPM_FW_SERVER.rpm"

# extract pre/post install/uninstall scripts
RUN rpm -qp --scripts "$RPM_FW_SERVER.rpm" | awk '/[preinstall|postinstall|preuninstall|postuninstall] scriptlet.*:/{x="F"++i;next;}{print > x;}' -
RUN mv F1 preinstall.sh && mv F2 postinstall.sh && mv F3 preuninstall.sh && mv F4 postuninstall.sh && chmod +x p*.sh
RUN cd / && rm -rf /install/*.rpm && rm -rf /install/*.zip

# stop the supervisord process ...
RUN /etc/init.d/fw-server stop

RUN cp -r /fwxserver/DB/pg_data /usr/local/filewave/tmp/pg_data
RUN cp -r /usr/local/filewave/certs /usr/local/filewave/tmp/certs

# NOTE: /fwxserver/DB/pg_data is NOT exposed as a volume as the current design calls for the data
# to be present within the container, only on export/import is it leaving the confines of its docker container.
#
# NOTE: grouping directories reduces the number of layers in the final image (a good thing)
VOLUME [ "/fwxserver", "/fwxserver/Data Folder", "/usr/local/filewave/apache/conf", "/usr/local/filewave/apache/logs", "/usr/local/filewave/apache/passwords", "/usr/local/filewave/certs", "/usr/local/filewave/fwcld", "/usr/local/filewave/django" ]
VOLUME [ "/usr/local/filewave/ipa", "/usr/local/filewave/log", "/usr/local/filewave/media", "/usr/local/filewave/postgresql/conf", "/usr/local/filewave/postgresql/log", "/usr/local/filewave/tmp", "/usr/local/filewave/scripts" ]

CMD [ "docker-entrypoint.sh" ]