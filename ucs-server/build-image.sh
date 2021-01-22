#!/bin/bash

set -ex

JENKINS_USER=jenkins-qa-uploader@filewave.com
JENKINS_PASSWORD=118f713b4f800f653125877cd353964c55

curl -u $JENKINS_USER:$JENKINS_PASSWORD -o ./fwxserver.rpm $downloadURL

docker build -t filewave/ucsserver:${FILEWAVE_VERSION} --build-arg FILEWAVE_VERSION=${FILEWAVE_VERSION} .

docker push filewave/ucsserver:${FILEWAVE_VERSION}
