from distutils.core import setup
setup(
  name = 'fwdocker',
  packages = ['fwdocker'], # this must be the same as the name above
  version = '0.1',
  description = 'A wrapper/utility to make it easy to use FileWave with Docker',
  author = 'John Clayton',
  author_email = 'johnc@filewave.com',
  url = 'https://github.com/johncclayton/fwdocker', # use the URL to the github repo
  download_url = 'https://github.com/johncclayton/fwdocker/tarball/0.1', # I'll explain this in a second
  keywords = ['filewave', 'docker', 'mdm', 'distribution'], # arbitrary keywords
  classifiers = [],
)
