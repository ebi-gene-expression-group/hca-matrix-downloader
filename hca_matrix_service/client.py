import argparse
import requests
import zipfile
import shutil
import json
import time
import re
import sys
import os


def parse_args():
    parser = argparse.ArgumentParser("Download data via HCA DCP FTP. Requires -p input.")
    parser.add_argument('-p', '--project',
                        help="The project's Project Title, Project short name or link-derived ID, obtained from the HCA DCP, wrapped in quotes.")
    parser.add_argument('-f', '--format', default="loom",
                        help="Format to download matrix in: loom, csv or mtx (Matrix Market). Defaults to loom.")
    parser.add_argument('-o', '--outprefix', default=None,
                        help="Output prefix for downloaded matrix. Leave default name (the Matrix API request ID) if not specified.")
    args = parser.parse_args()
    if not any(vars(args).values()):
        parser.error('No arguments provided.')
    return args


def get_project_uuid(project_arg):
    with open("hca_dcp_project_index.json", "r") as pi:
        project_index = json.load(pi)
    try:
        # if it is a uuid and its in the index, return the uuid
        if re.match('.{8}-.{4}-.{4}-.{4}-.{12}', project_arg) and project_index[project_arg]:
            return project_arg
        # if not a uuid, look up the uuid and return it
        return project_index[project_arg]
    except KeyError as e:
        print(e)
        print("The project " + str(e) + " was not found in the database. Please check the input and try again.")
        sys.exit()

def download_file(project_uuid):
    FTP_URL = "ftp://ftp.ebi.ac.uk/pub/databases/hca-dcp/dcp1_matrices"


def main():
    # parse the command line arguments
    args = parse_args()

    this_uuid = get_project_uuid(args.project)
    download_file(this_uuid)

    print("Contacting the Matrix API using the query: " + json.dumps(query))
    resp = requests.post(MATRIX_URL + "/matrix", json=query)
    # if there's no request_id field, something failed, report to user and abort
    if "request_id" not in resp.json().keys():
        raise ValueError("The Matrix API call failed with the following output: " + resp.text)
    request_id = resp.json()['request_id']
    print('Matrix API request ID: ' + request_id)
    while True:
        # check for doneness, the status will swap away from In Progress
        status_resp = requests.get(MATRIX_URL + "/matrix/" + resp.json()["request_id"])
        if status_resp.json()["status"] != "In Progress":
            break
        time.sleep(30)
    # did we succeed?
    if status_resp.json()['status'] == "Complete":
        # if we did, download the matrix
        matrix_response = requests.get(status_resp.json()["matrix_url"], stream=True)
        matrix_filename = os.path.basename(status_resp.json()["matrix_url"])
        with open(matrix_filename, 'wb') as matrix_file:
            shutil.copyfileobj(matrix_response.raw, matrix_file)
        # this used to come as a zip for everything, now loom just comes plain
        if args.format != 'loom':
            zipfile.ZipFile(matrix_filename).extractall()
            # for whatever crazy reason, the folder within the zip sometimes comes with a
            # different name than the request id. possibly some caching on their end.
            # rename to match our request ID
            os.rename(zipfile.ZipFile(matrix_filename).namelist()[0].split('/')[0], request_id + '.' + args.format)
            os.remove(matrix_filename)
        if args.outprefix:
            os.rename(
                '{}.{}'.format(request_id, args.format),
                '{}.{}'.format(args.outprefix, args.format))
    else:
        # something went wrong, spit out what and abort
        raise ValueError("The Matrix API call failed with the following output: " + status_resp.text)


if __name__ == "__main__":
    main()
