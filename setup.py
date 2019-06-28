from setuptools import setup, find_packages                                                                                                                                                                                                                              
  
with open('README.md', 'r') as fh:
    long_description = fh.read()

with open('VERSION', 'r') as fh:
    version = fh.read()

with open('requirements.txt', 'r') as fh:
    requirements = fh.readlines()

setup(
    name='hca_matrix_downloader',
    version=version,
    author='ktpolanski',
    author_email='ktpolanski@users.noreply.github.com',
    description='Python client for the HCA DCP matrix service',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ebi-gene-expression-group/hca-matrix-downloader',
    packages=find_packages(),
    scripts=[
        'hca-mtx-to-10x',
    ],
    entry_points=dict(
        console_scripts=[
            'hca-matrix-downloader=hca_matrix_service_client:main',
        ]
    ),
    install_requires=requirements,
)
