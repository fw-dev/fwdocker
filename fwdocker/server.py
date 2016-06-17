#!/usr/bin/env python
from subprocess import call
from ConfigParser import SafeConfigParser
import argparse, os, sys

# for configparser values
APP_SECTION = "APP"
VAR_FILEWAVE_VERSION = "FILEWAVE_VERSION"
VAR_FILEWAVE_DC_FILE = "FILEWAVE_DC_FILE"
VAR_LAST_COMMAND = "LAST_COMMAND"

__version__ = "0.1"

"""
This docker wrapper uses docker-compose to:
    - make a data volume to store the postgres data, configuration and log files
    - make a runtime FileWave MDM container and attach it to the data volume container

The wrapper makes it much easier to work with the FileWave MDM Server, instead of re-implementing shell, start, stop
and other commands - the wrapper outputs the required docker[-compose] command.

To kick off an all-in-one container for FileWave MDM, do this:
    # ./fwdocker.py --init

To run a shell within the FileWave container, do this on the terminal/cli:
    # $(./fwdocker.py --shell)

"""

def script_main(args=None):
    parser = argparse.ArgumentParser(description="A helper tool that makes using the FileWave Docker images easy.  You should" +
                                     " cut/paste the output of fwdocker into your terminal to run the command.",
                                     epilog="E.g. $(./fwdocker.py --init)")

    parser.add_argument("--init",
                        help="Initialise an all-in-one FileWave MDM Server using docker-compose",
                        action="store_true")
    parser.add_argument("--nosave",
                        help="dont store the runtime parameters, this is useful in testing or dev environments where you want to use multiple different container versions",
                        action="store_true")
    parser.add_argument("--shell",
                        help="Run a shell within the FileWave MDM Server runtime container",
                        action="store_true")
    parser.add_argument("--data",
                        help="Run a shell within the FileWave MDM Server data container",
                        action="store_true")
    parser.add_argument("--version",
                        help="Print the FileWave MDM Server version to the console, note: this requires the container to be running",
                        action="store_true")
    parser.add_argument("--logs",
                        help="Tail the logs for the FileWave MDM Server container",
                        action="store_true")
    parser.add_argument("--start",
                        help="Starts the FileWave MDM Server container",
                        action="store_true")
    parser.add_argument("--stop",
                        help="Stops the FileWave MDM Server container",
                        action="store_true")
    parser.add_argument("--info",
                        help="Show the stored version and docker-compose information that is stored in the ~/.fwdocker.ini file",
                        action="store_true")

    args = parser.parse_args(args=args)

    server_container_name = "fw_mdm_server"
    data_volume_name = "fw_mdm_data"

    if not args.init and not args.logs and not args.shell and not args.stop \
        and not args.start and not args.info and not args.data and not args.version:
        print "Try using ./fwdocker --init to fire up your first FileWave container!"
        sys.exit(1)

    # find the users .fwdocker settings file, see if we can get the FILEWAVE_VERSION
    # that is expected from there.  This will happen when the user does an --init
    settings_path = os.path.expanduser("~/.fwdocker.ini")

    # the config holds the version, which can always be overriden by the env var.
    config = SafeConfigParser(defaults={
        VAR_FILEWAVE_VERSION: "11.0.2",
        VAR_FILEWAVE_DC_FILE: "dc-allin1-data-volume.yml"
    })

    if os.path.exists(settings_path):
        config.read(settings_path)

    if not config.has_section(APP_SECTION):
        config.add_section(APP_SECTION)

    # if environment vars are present, these override the configuration specified values
    env_fw_version = os.environ.get('FILEWAVE_VERSION', None)
    env_dc_file = os.environ.get('FILEWAVE_DC_FILE', None)
    if env_fw_version is not None:
        config.set(APP_SECTION, VAR_FILEWAVE_VERSION, env_fw_version)
    if env_dc_file is not None:
        config.set(APP_SECTION, VAR_FILEWAVE_DC_FILE, env_dc_file)

    # create an environment var dict based on current values, and specify the
    # FILEWAVE_VERSION from the configuration (or override).
    env = dict(os.environ)
    env[VAR_FILEWAVE_VERSION] = fw_version = config.get(APP_SECTION, VAR_FILEWAVE_VERSION)
    env[VAR_FILEWAVE_DC_FILE] = dc_file = config.get(APP_SECTION, VAR_FILEWAVE_DC_FILE)

    if args.info:
        print "fwdocker.py Ini/Settings Info"
        print "============================="
        print VAR_FILEWAVE_VERSION, ":", env[VAR_FILEWAVE_VERSION]
        print VAR_FILEWAVE_DC_FILE, ":", env[VAR_FILEWAVE_DC_FILE]
        print VAR_LAST_COMMAND, ":", config.get(APP_SECTION, VAR_LAST_COMMAND)
        sys.exit(6)

    p = None
    if args.version:
        p = "docker exec -it %s /usr/local/sbin/fwxserver -V" % (server_container_name,)
    if args.init:
        p = "docker-compose -f %s -p fw up -d" % (dc_file,)
    if args.logs:
        p = "docker logs -f %s" % (server_container_name,)
    if args.shell:
        p = "docker exec -it %s /bin/bash" % (server_container_name,)
    if args.data:
        # this works efficiently because the common base image for both data/runtime volumes is centos:6.6
        p = "docker run -it --rm --volumes-from %s centos:6.6 /bin/bash" % (data_volume_name,)
    if args.stop:
        p = "docker-compose -f %s -p fw stop" % (dc_file,)
    if args.start:
        p = "docker-compose -f %s -p fw start" % (dc_file,)

    config.set(APP_SECTION, VAR_LAST_COMMAND, str(p))
    if not args.nosave:
        with open(settings_path, 'w') as w:
            config.write(w)

    if p:
        call(p.split(), env=env)
