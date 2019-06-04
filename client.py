import urllib.request
import subprocess
import requests
import argparse
import hca.dss
import json
import time
import os

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project', help="The project's Short Name, as seen in the HCA Data Browser entry, wrapped in quotes.")
    args = parser.parse_args()
    return args

def main():
    #load up project name
    args = parse_args()
    #set up DSS connection to download the sample info needed by the matrix API
    dsscli = hca.dss.DSSClient()
    #format the query, thankfully the only thing that changes is the project short name on input
    es_query = json.loads('{"query":{"bool":{"must":[{"match":{"files.project_json.project_core.project_short_name":"'
                          +args.project+'"}},{"match":{"files.analysis_process_json.process_type.text":"analysis"}}]}}}')
    # Collect fqids for the query from dss
    bundle_fqids = []
    try:
        for entry in dsscli.post_search.iterate(es_query=es_query, replica='aws'):
            bundle_fqids.append(entry['bundle_fqid'])
    except TypeError:
        #if the short name does not exist in the system, the above code bit tosses a TypeError
        raise ValueError("The specified project Short Name was not found in the database")
    #fire up a matrix API query
    url = 'https://matrix.data.humancellatlas.org/v0/matrix'
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    data = json.dumps({"bundle_fqids": bundle_fqids, "format": "loom"})
    r = requests.post(url, data=data, headers=headers)
    #now we have to keep checking if the matrix is available for download
    request_id = json.loads(r.content)['request_id']
    r = requests.get(url+'/'+request_id)
    while json.loads(r.content)['status'] == 'In Progress':
        time.sleep(30)
        r = requests.get(url+'/'+request_id)
    #the matrix is available. download it. done.
    urllib.request.urlretrieve(json.loads(r.content)["matrix_location"], "download.loom")

if __name__ == "__main__":
    main()
