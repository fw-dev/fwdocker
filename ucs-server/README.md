# MDM Server Container
This Docker container wraps all the FileWave MDM Server components in a single container.

# Build arguments
To build the container, run the build-image.sh script.  There are two dependencies:
  1. The FILEWAVE_VERSION environment variable, e.g. export FILEWAVE_VERSION=14.3.0
  2. The downloadURL environment variable that points to the server RPM to download, e.g. export downloadURL=https://jenkins.filewave.ch/job/master-Linux-CH/2862/artifact/BuildSystem/Packages/fwxserver-14.3.0-1.0.x86_64.rpm

# How to use this image

