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
    parser.add_argument('-s','--species', help="The species to use, when a project has more than one.",
                        default=None, required=False)
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
        print("The project identifier '{}' was not found in the database. Please check input and try again.".format(str(e)))
        sys.exit(1)


def download_file(project_uuid, file_format, prefix, project_info, species_to_use):
    file_address = project_info[file_format]
    files_dict = {fa: os.path.basename(fa) for fa in file_address}

    print("Found " + str(len(files_dict)) + " matrices to download.")

    species_list = [matrix_filename.split(".")[1] for ftp_a, matrix_filename in files_dict.items()]
    if len(species_list) > 1 and (not species_to_use or species_to_use not in species_list):
        print("Study has more than one species, so set the --species field to one of these values:")
        print(f"{species_list}")
        sys.exit(2)
    elif len(species_list) == 1:
        species_to_use = species_list[0]
    for ftp_address, matrix_filename in files_dict.items():
        species = matrix_filename.split(".")[1]
        if species != species_to_use:
            continue
        print("Downloading from " + ftp_address + ".")

        with urllib.request.urlopen(ftp_address) as response, open(matrix_filename, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        if file_format != 'loom':
            zipfile.ZipFile(matrix_filename).extractall()
            os.rename(zipfile.ZipFile(matrix_filename).namelist()[0].split('/')[0],
                      f"{project_uuid}.{species}.{file_format}")
            os.remove(matrix_filename)

        if prefix:
            os.rename(
                f'{project_uuid}.{species}.{file_format}',
                f'{prefix}.{file_format}'
            )

def main():
    # parse the command line arguments
    args = parse_args()
    loaded_index = load_project_index('ftp://ftp.ebi.ac.uk/pub/databases/hca-dcp/dcp1_matrices/hca_dcp_project_index.json')
    requested_project_uuid = get_project_uuid(args.project, loaded_index)
    download_file(requested_project_uuid, args.format, args.outprefix, loaded_index[requested_project_uuid], species_to_use=args.species)
    print("Project matrix data successfully downloaded.")
    sys.exit()


if __name__ == "__main__":
    main()
