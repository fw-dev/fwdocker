#!/usr/bin/env python

from subprocess import call
from ConfigParser import SafeConfigParser
import argparse, os, sys
from docker import Client

from pkg_resources import resource_filename

# for configparser values
APP_SECTION = "APP"

VAR_FILEWAVE_VERSION = "FILEWAVE_VERSION"
VAR_FILEWAVE_DC_FILE = "FILEWAVE_DC_FILE"
VAR_FILEWAVE_REPO_SERVER = "FILEWAVE_REPO_SERVER"
VAR_FILEWAVE_REPO_DATA = "FILEWAVE_REPO_DATA"

VAR_LAST_COMMAND = "LAST_COMMAND"

__version__ = "0.1"

"""
This docker wrapper uses docker-compose to:
    - make a data volume to store the postgres data, configuration and log files
    - make a runtime FileWave MDM container and attach it to the data volume container

This package installs the fwdocker command.

The command makes it easier to work with the FileWave MDM Server within Docker,
providing commands to bootstrap the containers as well as get access to them via shell.

To kick off an all-in-one container for FileWave MDM, do this:
    # fwdocker --init

To run a shell within the FileWave container, do this on the terminal/cli:
    # fwdocker --shell

"""
class ParamBuilder:
    def __init__(self, settings_path, docker_url='unix://var/run/docker.sock'):
        self.env = dict(os.environ)
        self.settings_path = settings_path
        # self.client = Client(docker_url)

        # the config holds the version, which can always be overriden by the env var.
        self.config = SafeConfigParser(defaults={
            VAR_FILEWAVE_VERSION: "11.0.2",
            VAR_FILEWAVE_DC_FILE: "dc-allin1-data-volume.yml",
            VAR_FILEWAVE_REPO_SERVER: "johncclayton/fw-mdm-server",
            VAR_FILEWAVE_REPO_DATA: "johncclayton/fw-mdm-data"
        })

        if os.path.exists(settings_path):
            self.config.read(settings_path)

        if not self.config.has_section(APP_SECTION):
            self.config.add_section(APP_SECTION)

        self.read_env_values()

    def get_param_value(self, param_name, default_value=None):
        value = os.environ.get(param_name, default_value)
        if value is not None:
            self.config.set(APP_SECTION, param_name, value)
            self.env[param_name] = value
        else:
            self.env[param_name] = self.config.get(APP_SECTION, param_name)
        return value

    def read_env_values(self):
        self.get_param_value(VAR_FILEWAVE_VERSION)
        self.get_param_value(VAR_FILEWAVE_DC_FILE)
        self.get_param_value(VAR_FILEWAVE_REPO_SERVER)
        self.get_param_value(VAR_FILEWAVE_REPO_DATA)

        # pull the DC file, and validate it exists, if not extract the one we've got
        # in the package and write it to the Python egg cache
        env_dc_file = self.config.get(APP_SECTION, VAR_FILEWAVE_DC_FILE)
        if not os.path.exists(env_dc_file):
            env_dc_file = resource_filename(__name__, env_dc_file)
            if os.path.exists(env_dc_file):
                self.config.set(APP_SECTION, VAR_FILEWAVE_DC_FILE, env_dc_file)
                self.env[VAR_FILEWAVE_DC_FILE] = env_dc_file



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
        print "Use ./fwdocker --init to fire up your first FileWave container, or --help for more information"
        sys.exit(1)

    # find the users .fwdocker settings file, see if we can get the FILEWAVE_VERSION
    # that is expected from there.  This will happen when the user does an --init
    settings_path = os.path.expanduser("~/.fwdocker.ini")
    param = ParamBuilder(settings_path)

    if args.info:
        print "fwdocker.py Settings"
        print "===================="
        print VAR_FILEWAVE_VERSION, ":", param.env[VAR_FILEWAVE_VERSION]
        print VAR_FILEWAVE_DC_FILE, ":", param.env[VAR_FILEWAVE_DC_FILE]
        print VAR_FILEWAVE_REPO_SERVER, ":", param.env[VAR_FILEWAVE_REPO_SERVER]
        print VAR_FILEWAVE_REPO_DATA, ":", param.env[VAR_FILEWAVE_REPO_DATA]
        print VAR_LAST_COMMAND, ":", param.config.get(APP_SECTION, VAR_LAST_COMMAND)
        sys.exit(6)

    p = None
    if args.version:
        p = "docker exec -it %s /usr/local/sbin/fwxserver -V" % (server_container_name,)
    if args.init:
        print "Initializing a FileWave Server, version:", param.env[VAR_FILEWAVE_VERSION]
        print "Tip: use fwdocker --logs, to monitor the logs of the new container called: %s" % (server_container_name)
        p = "docker-compose -f %s -p fw up -d" % (param.env[VAR_FILEWAVE_DC_FILE],)
    if args.logs:
        p = "docker logs -f %s" % (server_container_name,)
    if args.shell:
        p = "docker exec -it %s /bin/bash" % (server_container_name,)
    if args.data:
        # this works efficiently because the common base image for both data/runtime volumes is centos:6.6
        p = "docker run -it --rm --volumes-from %s centos:6.6 /bin/bash" % (data_volume_name,)
    if args.stop:
        p = "docker-compose -f %s -p fw stop" % (param.env[VAR_FILEWAVE_DC_FILE],)
    if args.start:
        p = "docker-compose -f %s -p fw start" % (param.env[VAR_FILEWAVE_DC_FILE],)

    param.config.set(APP_SECTION, VAR_LAST_COMMAND, str(p))
    if not args.nosave:
        with open(settings_path, 'w') as w:
            param.config.write(w)

    if p:
        call(p.split(), env=param.env)
