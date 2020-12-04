import argparse
import requests
import zipfile
import shutil
import json
import time
import re
import sys
import os
import urllib.request


def parse_args():
    parser = argparse.ArgumentParser("Download data via HCA DCP FTP. Requires -p input. Files are downloaded into "
                                     "current working directory.")
    parser.add_argument('-p', '--project',
                        help="The project's Project Title, Project short name or link-derived ID, obtained from the "
                             "HCA DCP, wrapped in quotes.")
    parser.add_argument('-f', '--format', default="loom", choices=["loom", "mtx"],
                        help="Format to download matrix in: loom, csv or mtx (Matrix Market). Defaults to loom.")
    parser.add_argument('-o', '--outprefix', default=None,
                        help="Output prefix for downloaded matrix. Leave default name (the Matrix API request ID) if "
                             "not specified.")
    args = parser.parse_args()
    if not any(vars(args).values()):
        parser.error('No arguments provided.')
    return args


def get_project_uuid(project_arg):
    with open("hca_dcp_project_index.json", "r") as pi:
        project_index = json.load(pi)
    try:
        # if uuid provided and it is in the index, return the uuid
        if re.match('.{8}-.{4}-.{4}-.{4}-.{12}', project_arg) and project_index[project_arg]:
            print("Project uuid '" + project_arg + "' found with title '" +
                  project_index[project_arg]['project.project_core.project_title'] + "'.")
            return project_arg
        # if not a uuid, look up the uuid and return it
        print("Project '" + project_arg + "' found with uuid '" + project_index[project_arg] + "'.")
        return project_index[project_arg]
    except KeyError as e:
        print(e)
        print("The project identifier " + str(e) + " was not found in the database. Please check input and try again.")
        sys.exit()


def download_file(project_uuid, file_format, prefix):
    ftp_url = "ftp://ftp.ebi.ac.uk/pub/databases/hca-dcp/dcp1_matrices/"
    if file_format is "mtx":
        file_extension = "mtx.zip"
    else:
        file_extension = "loom"
    matrix_filename = project_uuid + "." + file_extension
    file_address = ftp_url + matrix_filename

    with urllib.request.urlopen(file_address) as response, open(matrix_filename, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

    if file_format != 'loom':
        zipfile.ZipFile(matrix_filename).extractall()
        # for whatever crazy reason, the folder within the zip sometimes comes with a
        # different name than the request id. possibly some caching on their end.
        # rename to match our request ID
        os.rename(zipfile.ZipFile(matrix_filename).namelist()[0].split('/')[0], project_uuid + '.' + file_format)
        os.remove(matrix_filename)

    if prefix:
        os.rename(
            '{}.{}'.format(project_uuid, file_format),
            '{}.{}'.format(prefix, file_format)
        )

def main():
    # parse the command line arguments
    args = parse_args()
    requested_project_uuid = get_project_uuid(args.project)
    download_file(requested_project_uuid, args.format, args.outprefix)


if __name__ == "__main__":
    main()
