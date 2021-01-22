FROM centos:7

LABEL "maintainer"="support@filewave.com"

ARG FILEWAVE_VERSION
ENV FILEWAVE_VERSION ${FILEWAVE_VERSION:-12.0.0}

# Analytics uses this one to detect if it's a UCS instance
ENV FILEWAVE_INSIDE_DOCKER_VERSION=${FILEWAVE_VERSION}

ENV FILEWAVE_ON_UCS=1

EXPOSE 19995 19996 20005 20006 20015 20016 20017 20030 20443 20445 20446

RUN mkdir -p /install
WORKDIR /install
COPY fwxserver.rpm ./

RUN yum install -y initscripts && \
    yum install -y --nogpgcheck /install/fwxserver.rpm && \
    yum clean all && \
    rm -rf /var/cache/* && \
    /usr/local/sbin/fwxserver -V > /PRODUCT_VERSION && \
    /usr/local/sbin/fwxserver -VV >> /PRODUCT_VERSION && \
    /etc/init.d/fw-server stop && \
    killall fwsu || true && \
    rm -rf /tmp/*

WORKDIR /
RUN rm -rf /install

# Copy all the FW directories in the temporary space
RUN mkdir -p /tmp/filewave && \
    cp -r /usr/local/filewave/fwxserver/DB \
    /usr/local/filewave/fwxserver/"Data Folder" \
    /usr/local/filewave/certs \
    /usr/local/filewave/fwcld \
    /usr/local/filewave/apache/conf \
    /usr/local/etc \
    /tmp/filewave/

# Copy user_postgresql.conf, it should be in one of these places
RUN mkdir -p /tmp/filewave/postgres_conf
RUN cp -r /usr/local/filewave/conf/* \
    /usr/local/filewave/postgresql/conf/* \
    /tmp/filewave/postgres_conf/ 2> /dev/null || true

# NOTE: grouping directories reduces the number of layers in the final image (a good thing)
VOLUME [ \
    "/usr/local/filewave/fwxserver/DB", \
    "/usr/local/filewave/fwxserver/Data Folder", \
    "/usr/local/filewave/postgresql/conf", \
    "/usr/local/filewave/apache/conf", \
    "/usr/local/filewave/apache/logs", \
    "/usr/local/filewave/apache/passwords", \
    "/usr/local/filewave/certs", \
    "/usr/local/filewave/fwcld",  \
    "/usr/local/filewave/ipa", \
    "/usr/local/filewave/log", \
    "/usr/local/filewave/media", \
    "/usr/local/filewave/tmp/", \
    "/usr/local/etc" \
    ]

COPY ./docker-entrypoint.sh /
# overwrite the supervisord configuration to not use core dumps:
COPY supervisord-server-docker-full.conf /usr/local/etc/filewave/supervisor/supervisord-server-full.conf

ENTRYPOINT [ "/docker-entrypoint.sh" ]
