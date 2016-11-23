#!/usr/bin/env bash

export FILEWAVE_VERSION=11.2.2
export LINUX_ZIPFILE_NAME=FileWave_Linux_${FILEWAVE_VERSION}.zip

if [ ! -f $LINUX_ZIPFILE_NAME ]; then
    echo Cant build - put the linux zip file in this directory
    echo Linux ZIP Filename: $LINUX_ZIPFILE_NAME
    exit 2
else
    docker build -t filewave/mdm-server:${FILEWAVE_VERSION} .
    # docker push filewave/mdm-server:11.2.2
fi

