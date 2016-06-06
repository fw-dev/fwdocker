#!/usr/bin/env python
import argparse, sys, os, json

# from operator import itemgetter, attrgetter, methodcaller

try:
    from docker import Client, errors

    docker_available = True
except ImportError:
    docker_available = False

if not docker_available:
    print "please make sure to install docker-py via pip before using this package"
    print "e.g: sudo pip install docker-py"
    sys.exit(1)

FW_MDM_SERVER_IMAGE = "johncclayton/fw-mdm-server"
FW_MDM_DATA_IMAGE = "johncclayton/fw-mdm-data-volume"


class FileWaveDockerApi:
    def __init__(self, tag="latest", docker_url='unix://var/run/docker.sock'):
        self.tag = tag
        self.client = Client(base_url=docker_url)
        self.data_volume_image = FW_MDM_DATA_IMAGE
        self.data_volume_name = "fw-mdm-data-volume"
        self.server_image = FW_MDM_SERVER_IMAGE
        if self.tag is not None:
            self.server_image += ":" + self.tag
        self.server_name = "fw-mdm-server"
        self.server_ports = []
        self.port_bindings = {}

        fw_version = self.get_filewave_version_for_image(self.server_image)
        if fw_version is not None:
            self.server_name = "fw-mdm-server-" + fw_version

    def store_exposed_ports_for_image(self, name):
        image = self.find_image_named(name)
        if not image:
            return False
        config = self.client.inspect_image(image)
        if not config:
            return False
        if "Config" in config and "ExposedPorts" in config["Config"]:
            ports = config["Config"]["ExposedPorts"]
            self.server_ports = [int(k[:-4]) for k in ports.keys()]
            self.port_bindings = {x: x for x in self.server_ports}
            return True
        return False

    def __get_filewave_version(self, image):
        if image is None:
            return None
        config = self.client.inspect_image(image)
        if not config:
            return None
        if "Config" in config and "Env" in config["Config"]:
            for var in config["Config"]["Env"]:
                name, value = var.split("=")
                if name == "FILEWAVE_VERSION":
                    return value
        return None

    def get_filewave_version_for_image(self, name):
        return self.__get_filewave_version(self.find_image_named(name))

    def find_container_named(self, container_name):
        for c in self.client.containers(all=True, filters={'name': container_name}):
            return c
        return None

    def find_image_named(self, image_name):
        for c in self.client.images(name=image_name):
            return c
        return None

    def create_data_volume_container(self):
        return self.client.create_container(image=self.data_volume_image,
                                            name=self.data_volume_name,
                                            command="/bin/true")

    def create_server_container(self):
        if not self.store_exposed_ports_for_image(self.server_image):
            return None

        config = self.client.create_host_config(
            cap_add=['ALL'],  # not sure if this is required on centos:6.6, it is for 6.7 and 7.x series.
            privileged=True,
            port_bindings=self.port_bindings,
            publish_all_ports=True,
            volumes_from=self.data_volume_name
        )

        image_exec = self.client.create_container(self.server_image,
                                                  ports=self.server_ports,
                                                  detach=True,
                                                  host_config=config,
                                                  name=self.server_name
                                                  )

        return image_exec

    def tail_server_logs(self):
        container = self.find_container_named(self.server_name)
        if not container:
            return False
        return self.client.logs(container=container.get('Id'), stream=True, timestamps=True, follow=True)


"""
This docker wrapper will always:
    - make a data volume to store the postgres database, configuration and log files
    - make a runtime FileWave MDM container and attach it to the data volume container

The wrapper makes it much easier to work with the FileWave MDM Server, instead of re-implementing shell, start, stop
and other commands - the wrapper outputs the required docker command.

To run a shell within the FileWave container, do this on the terminal/cli:
    # $(./fwdocker -s)

"""
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

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

    try:
        # this is the version of the image to get - the code will still look in the image meta data to obtain
        # the actual version so that this is what gets appended to the server container docker name
        api = FileWaveDockerApi(tag=os.getenv("FILEWAVE_VERSION", "latest"))

        # find the data container we need.  if not pull it down.
        data_container = api.find_container_named(api.data_volume_name)
        if not data_container:
            data_container = api.create_data_volume_container()

        if not api.find_image_named(api.server_image):
            print "cannot create server - image not found:", api.server_image
            sys.exit(3)
        else:
            # does the container already exist, so that we can just start it?
            server_container = api.find_container_named(api.server_name)
            if not server_container:
                server_container = api.create_server_container()

            if server_container:
                api.client.start(container=server_container.get('Id'))
            else:
                print "problem creating container"
                sys.exit(2)

        if args.logs:
            print "docker logs -f", api.server_name
        if args.shell:
            print "docker exec -it", api.server_name, "/bin/bash"
        if args.stop:
            print "docker stop", api.server_name
        if args.start:
            print "docker start", api.server_name
        if args.data:
            print "docker run -it --rm --volumes-from", api.data_volume_name, " centos:6.6 /bin/bash"

    except errors.NotFound, e:
        print "An image wasn't found - you will need to 'docker pull <name name>:<tag>'"
        print e
