import argparse
import requests
import zipfile
import shutil
import json
import time
import sys
import os

def parse_args():
	parser = argparse.ArgumentParser("Download data via HCA's Matrix API V1. Requires either -p or -q input.")
	parser.add_argument('-p', '--project', help="The project's Project Title, Project Label or link-derived ID, obtained from the HCA DCP, wrapped in quotes.")
	parser.add_argument('-q', '--query', help="A complete /v1/matrix/ POST query in JSON format. Consult https://matrix.dev.data.humancellatlas.org/ for details.")
	args = parser.parse_args()
	if not any(vars(args).values()):
		parser.error('No arguments provided.')
	return args

def main():
	#parse the command line arguments
	args = parse_args()
	#the Matrix API is located here
	MATRIX_URL = "https://matrix.data.humancellatlas.org/v1"
	if args.query:
		#the user provided a query on input, parse it into a JSON and we're done
		query = json.loads(args.query)
	else:
		#the user provided a project name, start by determining the type of name
		found = False
		for project_type in ["project.provenance.document_id",
							 "project.project_core.project_short_name",
							 "project.project_core.project_title"]:
			#get the list of all available IDs for the potential type of name
			resp = requests.get(MATRIX_URL+"/filters/"+project_type)
			#is our project here?
			if args.project in list(resp.json()['cell_counts'].keys()):
				#if so, flag that we matched the name type
				found = True
				break
		#we failed to locate our project in the database, abort downloader
		if not found:
			raise ValueError("The specified project was not found in the database")
		#construct our JSON query, matching the formal formatting requirements
		query = {"filter":
					{"op": "=",
					 "value": args.project,
					 "field": project_type
				}}
	#fire up the query at the Matrix API
	print("Contacting the Matrix API using the query: "+json.dumps(query))
	resp = requests.post(MATRIX_URL+"/matrix", json=query)
	#if there's no request_id field, something failed, report to user and abort
	if "request_id" not in resp.json().keys():
		raise ValueError("The Matrix API call failed with the following output: "+resp.text)
	while True:
		#check for doneness, the status will swap away from In Progress
		status_resp = requests.get(MATRIX_URL+"/matrix/"+resp.json()["request_id"])
		if status_resp.json()["status"] != "In Progress":
			break
		time.sleep(30)
	#did we succeed?
	if status_resp.json()['status'] == "Complete":
		#if we did, download the matrix
		matrix_response = requests.get(status_resp.json()["matrix_url"], stream=True)
		matrix_zip_filename = os.path.basename(status_resp.json()["matrix_url"])
		with open(matrix_zip_filename, 'wb') as matrix_zip_file:
			shutil.copyfileobj(matrix_response.raw, matrix_zip_file)
		#this comes as a zip, extract the contents and lose the archive
		zipfile.ZipFile(matrix_zip_filename).extractall()
		os.remove(matrix_zip_filename)
	else:
		#something went wrong, spit out what and abort
		raise ValueError("The Matrix API call failed with the following output: "+status_resp.text)

if __name__ == "__main__":
	main()