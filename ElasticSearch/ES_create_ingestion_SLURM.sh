#!/bin/bash

#SBATCH --job-name=ES_ingest_xml
#SBATCH --nodes=1
#SBATCH --tasks-per-node=16
#SBATCH --time=00:30:00
#SBATCH --export=NONE

set -e # Good Idea to stop operation on first error.

source /sw/batch/init.sh

# Load environment modules for your application here.
module load python/3.6.8
module load java/oracle-jdk8u101

srun python3 $HOME/scripts/ElasticSearch/elasticsearch_create_ingestion_xml_files.py formulae 16
