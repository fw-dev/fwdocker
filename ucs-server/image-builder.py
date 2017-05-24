import os
import os.path

import docker
import logging
import requests
import glob
import shutil
import zipfile


def get_build_params():

    base_dir = os.path.dirname(os.path.realpath(__file__))
    tag_name = os.getenv('IMAGE_TAG')
    workspace = os.getenv('WORKSPACE')
    repository_name = 'filewave/ucsserver'

    data_file = os.path.join(workspace, 'filewave_linux.zip')

    logging.info('Extracting FILEWAVE_VERSION from %s', data_file)
    with zipfile.ZipFile(data_file, 'r') as infile:
        for zipinfo in infile.infolist():
            tokens = zipinfo.filename.split('-')
            if tokens[0] == 'fwxserver':
                filewave_version = tokens[1]
                break

    logging.info('FILEWAVE_VERSION: %s', filewave_version)
    
    params = {
        'repository_name': repository_name,
        'tag_name': tag_name,
        'image_tag': '{}:{}'.format(repository_name, tag_name),
        'filewave_version': filewave_version,
        'workspace': workspace,
        'data_file': data_file,
        'input_file': os.path.join(base_dir, 'FileWave_Linux_{}.zip'.format(filewave_version)),
        'base_dir': base_dir,
    }

    return params


def build_docker_image(client, params):

    os.chdir(params['base_dir'])

    # Remove any previous data file
    for in_file in glob.glob('FileWave_Linux_*.zip'):
        os.remove(in_file)

    # COPY and rename the file
    shutil.copyfile(params['data_file'], params['input_file'])

    # Build the image
    logging.info('Building the Image %s...', params['image_tag'])
    client.images.build(
        path='.',
        quiet=False,
        tag=params['image_tag'],
        buildargs=dict(FILEWAVE_VERSION=params['filewave_version'])
    )
    logging.info('Image %s built successfully', params['image_tag'])


def push_on_docker_hub(client, params):
    
    # Login into hub.docker.com
    # logging.info('Loggin In https://hub.docker.com')
    # client.login()
    # logging.info('Logged In')

    logging.info('Pushing image %s to https://hub.docker.com...', params['image_tag'])
    for line in client.images.push(params['repository_name'], tag=params['tag_name'], stream=True):
        logging.debug('> %s', line)

    logging.info('Image %s pushed successfully', params['image_tag'])

def main():

    # Connects to the Docker Engine
    client = docker.from_env()
    client.ping()

    logging.info('Connected to the Docker Engine')

    # Get Build params
    params = get_build_params()

    # Build the Image
    build_docker_image(client, params)

    # Publish on DockerHub
    push_on_docker_hub(client, params)

    logging.info('Done')


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)

    try:
        main()

    except requests.exceptions.ConnectionError:
        logging.error('Error connecting to the docker engine')

    except docker.errors.APIError as ex:
        logging.error('API Error: %s', ex)
