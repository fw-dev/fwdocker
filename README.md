# fwdocker 
This is a program that makes it easy to install a docker version of the FileWave MDM product. 

The program provides the ability to: 
 1. start a FileWave MDM Server with an attached data volume (this is best practise)
 2. access the server via a standard Unix shell
 3. access the attached data volume via a standard Unix shell
 4. use basic commands on the service such as start / stop 
 5. obtain logging information
 
FileWave MDM is split into two parts - a data container, and a runtime container.  The data container holds the
configuration, database, certificates and logs etc.  The data container is what is used to back up a FileWave installation. 

The runtime container holds all the binaries for a particular version of FileWave, and attaches to the data container.  

By separating out the data from the runtime its easy to backup and upgrade your FileWave installation on Docker.

# Getting Started
To run FileWave, simply type this: 

    # ./fwdocker.py --init <filewave version, default is "11.2.1">
    
This will:
  1. create a data volume container if it doesn't already exist
  2. create a runtime container for the FileWave MDM system and link with the data volume
  3. start the FileWave MDM system - please note, the first time can take 5-10 minutes while components are installed and configured
 
# What can fwdocker do?
The purpose of fwdocker.py is to simplifying using Docker to run FileWave.  By using fwdocker you will easily get a 
FileWave MDM system up and running in minutes.

Use the -h (or --help) command to get a description of the commands that fwdocker accepts.

## Upgrading / Migration
Upgrades and migrations ONLY occur automatically when the container is started for the first time.  This is
 is when the appropriate binaries are downloaded, unpacked and installed via RPM. 
 
## Accessing the Data Volume via Terminal
Use fwdocker.py to spawn a shell attached to the data volume - in this instance you will NOT see any of the 
 runtime associated with the FileWave MDM Server.  To do this, run the following command:

    # $(./fwdocker.py --data)
    
## Accessing the FileWave MDM Server via Terminal
Use fwdocker.py to spawn a shell attached to the FileWave MDM Server:

    # $(./fwdocker.py --shell)


## Publishing the package to PyPi
Please check the following link for more information: http://peterdowns.com/posts/first-time-with-pypi.html

If you want to publish a new version, remember to increment the version in fwdocker/fwdocker.py - otherwise
the sdist upload command will fail.

To publish, do the following two steps with any python interpreter:

  $ python setup.py build
  $ python setup.py sdist upload -r pypitest

When the world is in order and things work, e.g. you have checked out that the code works on the staging PyPi services
available here https://testpypi.python.org/pypi, then you can publish to the world at large:

  $ python setup.py sdist upload pypi

