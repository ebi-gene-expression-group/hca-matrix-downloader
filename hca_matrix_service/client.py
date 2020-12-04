import argparse
import zipfile
import shutil
import json
import re
import sys
import os
import urllib.request


def parse_args():
    parser = argparse.ArgumentParser("Download data via HCA DCP FTP. Requires -p input. Files are downloaded into "
                                     "current working directory.")
    parser.add_argument('-p', '--project',
                        help="The project's Project Title, Project short name or link-derived ID, obtained from the "
                             "HCA DCP, wrapped in quotes.", required=True)
    parser.add_argument('-f', '--format', default="loom", choices=["loom", "mtx"],
                        help="Format to download matrix in: loom or mtx (Matrix Market). Defaults to loom.")
    parser.add_argument('-o', '--outprefix', default=None,
                        help="Output prefix to replace project uuid in filename of downloaded matrix. Leave as project "
                             "uuid if not specified.")
    args = parser.parse_args()
    return args


def load_project_index(path):
    with urllib.request.urlopen(path) as response:
        project_index = json.load(response)
    return project_index

def get_project_uuid(project_arg, project_index):
    try:
        # if uuid provided and it is in the index, return the uuid
        if project_index[project_arg] and re.match('.{8}-.{4}-.{4}-.{4}-.{12}', project_arg):
            print("Project uuid '{}' found with title '{}'.".format(project_arg, project_index[project_arg]
                  ['project.project_core.project_title']))
            return project_arg
        # if not a uuid, look up the uuid and return it
        print("Project '{}' found with uuid '{}'.".format(project_arg, project_index[project_arg]))
        return project_index[project_arg]
    except KeyError as e:
        print(e)
        print("The project identifier " + str(e) + " was not found in the database. Please check input and try again.")
        sys.exit()


def download_file(project_uuid, file_format, prefix, project_info):
    file_address = project_info[file_format]
    files_dict = {fa: os.path.basename(fa) for fa in file_address}

    print("Found " + str(len(files_dict)) + " matrices to download.")

    for ftp_address, matrix_filename in files_dict.items():
        print("Downloading from " + ftp_address + ".")
        species = matrix_filename.split(".")[1]
        with urllib.request.urlopen(ftp_address) as response, open(matrix_filename, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        if file_format != 'loom':
            zipfile.ZipFile(matrix_filename).extractall()
            species = matrix_filename.split(".")[1]
            os.rename(zipfile.ZipFile(matrix_filename).namelist()[0].split('/')[0], project_uuid + '.' + species + '.'
                      + file_format)
            os.remove(matrix_filename)

        if prefix:
            os.rename(
                '{}.{}.{}'.format(project_uuid, species, file_format),
                '{}.{}.{}'.format(prefix, species, file_format)
            )

def main():
    # parse the command line arguments
    args = parse_args()
    # loaded_index = load_project_index(path)
    with open("hca_dcp_project_index.json", "r") as pi:
        loaded_index = json.load(pi)
    requested_project_uuid = get_project_uuid(args.project, loaded_index)
    download_file(requested_project_uuid, args.format, args.outprefix, loaded_index[requested_project_uuid])
    print("Project matrix data successfully downloaded.")
    sys.exit()


if __name__ == "__main__":
    main()
