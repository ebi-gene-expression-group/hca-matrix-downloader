# Human Cell Atlas Matrix Client

This small cli enables the retrieval of Human Cell Atlas matrices from an ftp folder for a particular experiment in either
Loom or Matrix market format.

1. Go to the HCA Data Browser: https://data.humancellatlas.org/explore/projects
2. Under "Search", write in "matrix". This will limit the projects to those supporting the matrix formatting
3. Click on a project of interest in the list, e.g. this one: https://data.humancellatlas.org/explore/projects/cddab57b-6868-4be4-806f-395ed9dd635a
4. Call the downloader, providing either one of the project names (Project Title, Project Label or the ID from the link). 

Any of these arguments would work:

```
-p "Single cell transcriptome analysis of human pancreas"
-p "Single cell transcriptome analysis of human pancreas reveals transcriptional signatures of aging and somatic mutation patterns."
-p cddab57b-6868-4be4-806f-395ed9dd635a
```

For complete usage information, use `-h`.

A shell script for converting HCA mtx to 10X(v2)-compatible mtx is provided.
