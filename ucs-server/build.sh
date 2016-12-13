#!/usr/bin/env bash

# FILEWAVE_VERSION=12.0.0
FILEWAVE_VERSION=${1:-12.0.0}
LINUX_ZIPFILE_NAME=FileWave_Linux_${FILEWAVE_VERSION}.zip

if [ ! -f $LINUX_ZIPFILE_NAME ]; then
    echo Cant build - put the linux zip file in this directory
    echo Linux ZIP Filename: $LINUX_ZIPFILE_NAME
    exit 2
else
    docker build -t filewave/ucsserver:${FILEWAVE_VERSION} --build-arg FILEWAVE_VERSION=${FILEWAVE_VERSION} .
fi

