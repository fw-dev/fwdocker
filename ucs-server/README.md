# MDM Server Container
This Docker container wraps all the FileWave MDM Server components in a single container.

# Build arguments
To build the container, run the build.sh script.  There are two dependancies:
  1. The FILEWAVE_VERSION environment variable value, e.g. export FILEWAVE_VERSION=11.2.3
  2. The downloaded Linux RPM in its artifact ZIP file (dont unpack it) - e.g. FileWave_Linux_11.2.3.zip

# ZIP File
To get the right Linux ZIP file - just download the artifacts of a Linux build from our repo.

# How to use this image

