#!/usr/bin/env python
import argparse, sys, subprocess

try:
    from docker import Client
    docker_available = True
except ImportError:
    docker_available = False

if not docker_available:
    print "please make sure to install docker-py via pip before using this package"
    print "e.g: sudo pip install docker-py"
    sys.exit(1)

class FileWaveDockerApi:
    def __init__(self, version="11.0.2", docker_url='unix://var/run/docker.sock'):
        self.version = version
        self.client = Client(base_url=docker_url)
        self.data_volume_image = "johncclayton/fw-mdm-data-volume"
        self.data_volume_name = "fw-mdm-data-volume"
        self.server_image = "johncclayton/fw-mdm-server"
        self.server_name = "fw-mdm-server-" + self.version
        self.server_ports = []
        self.port_bindings = {}

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
                                            command="/bin/true"
                                            )

    def create_server_container(self):
        if not self.store_exposed_ports_for_image(self.server_image):
            return None

        config = self.client.create_host_config(
            cap_add=['ALL'], # not sure if this is required on centos:6.6, it is for 6.7 and 7.x series.
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

    parser.add_argument("--shell", help="outputs the required docker command to run a shell within the FileWave MDM Server and attached data volume", action="store_true")
    parser.add_argument("--data", help="outputs the required docker command to run a shell which is mapped ONLY to the data-volume", action="store_true")
    parser.add_argument("--logs", help="outputs the required docker command to tail the container logs", action="store_true")
    parser.add_argument("--start", help="outputs the required docker command to start the container", action="store_true")
    parser.add_argument("--stop", help="outputs the required docker command to stop the container", action="store_true")

    args = parser.parse_args()

    api = FileWaveDockerApi()

    # always create the required data volume and create the runtime container as well.
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
