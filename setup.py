from setuptools import setup, find_packages                                                                                                                                                                                                                              
  
with open('README.md', 'r') as fh:
    long_description = fh.read()

with open('VERSION', 'r') as fh:
    version = fh.read()

with open('requirements.txt', 'r') as fh:
    requirements = fh.readlines()

setup(
    name='hca_dcp_client',
    version=version,
    author='ktpolanski',
    author_email='ktpolanski@users.noreply.github.com',
    description='Python client for the DCP matrix service',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ebi-gene-expression-group/dcp-matrix-service-client',
    packages=find_packages(),
    scripts=[
        'hca_matrix_service_client.py',
    ],
    install_requires=requirements,
)
