#!/usr/bin/env python
import argparse

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
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--init",
                        help="outputs the command required to initialise an all-in-one FileWave MDM Server using docker-compose",
                        action="store_true")
    parser.add_argument("--shell",
                        help="outputs the required docker command to run a shell within the FileWave MDM Server and attached data volume",
                        action="store_true")
    parser.add_argument("--data",
                        help="outputs the required docker command to run a shell which is mapped ONLY to the data-volume",
                        action="store_true")
    parser.add_argument("--logs", help="outputs the required docker command to tail the container logs",
                        action="store_true")
    parser.add_argument("--start", help="outputs the required docker command to start the container",
                        action="store_true")
    parser.add_argument("--stop", help="outputs the required docker command to stop the container", action="store_true")

    args = parser.parse_args()

    server_name = "fw_mdm_server_1"
    data_volume_name = "fw_mdm_data_1"

    if args.init:
        print "docker-compose -f dc-allin1-data-volume.yml -p fw up -d"
    if args.logs:
        print "docker logs -f", server_name
    if args.shell:
        print "docker exec -it", server_name, "/bin/bash"
    if args.stop:
        print "docker-compose -f dc-all-in-one.yml -p fw stop"
    if args.start:
        print "docker-compose -f dc-all-in-one.yml -p fw start"
    if args.data:
        print "docker run -it --rm --volumes-from", data_volume_name, " centos:6.6 /bin/bash"
