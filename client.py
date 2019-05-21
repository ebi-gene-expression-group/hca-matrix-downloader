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
    args = parse_args()
    dsscli = hca.dss.DSSClient()
    es_query = json.loads('{"query":{"bool":{"must":[{"match":{"files.project_json.project_core.project_short_name":"'+args.project+'"}},{"match":{"files.analysis_process_json.process_type.text":"analysis"}}]}}}')
    manifest = ['bundle_uuid\tbundle_version\n']
    for entry in dsscli.post_search.iterate(es_query=es_query, replica='aws'):
        entry_split = entry['bundle_fqid'].split('.')
        manifest.append(entry_split[0]+'\t'+entry_split[1]+'.'+entry_split[2]+'\n')
    with open('ids.txt','w') as fid:
        fid.writelines(manifest)
    res = subprocess.run('curl -F "file=@ids.txt" https://file.io', shell=True, stdout=subprocess.PIPE)
    os.remove('ids.txt')
    manifest_url = json.loads(res.stdout.decode('utf-8'))['link']
    url = 'https://matrix.data.humancellatlas.org/v0/matrix'
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    data = json.dumps({"bundle_fqids_url": manifest_url, "format": "loom"})
    r = requests.post(url, data=data, headers=headers)
    request_id = json.loads(r.content)['request_id']
    r = requests.get(url+'/'+request_id)
    while json.loads(r.content)['status'] == 'In Progress':
        time.sleep(30)
        r = requests.get(url+'/'+request_id)
    urllib.request.urlretrieve(json.loads(r.content)["matrix_location"], "download.loom")

if __name__ == "__main__":
    main()