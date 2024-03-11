
from gcs_to_mongo import *
from get_jobs_from_api import *
from convert_to_embeddings import *
from summary_statistics import *
from airflow.operators.python import PythonOperator
from airflow import DAG
from datetime import datetime
import os
import sys


# Define the DAG for the search engine pipeline
with DAG(
    dag_id="job-recommender",
    start_date=datetime(2024, 3, 5),
    schedule_interval="@daily",
) as dag:

    os.environ["no_proxy"] = "*"

    get_jobs_op = PythonOperator(
        task_id="get_jobs_data", python_callable=get_data
    )

    gcs_to_mongo_op = PythonOperator(
        task_id="gcs_to_mongo", python_callable=gcs_to_mongodb_collection
    )

    summary_statistics_op = PythonOperator(
        task_id="summary_statistics", python_callable=calculate_summary_statistics
    )

    convert_to_embeddings_op = PythonOperator(
        task_id="convert_to_embeddings", python_callable=embed_descriptions
    )

    # Set the task dependencies
    get_jobs_op >> gcs_to_mongo_op >> convert_to_embeddings_op >> summary_statistics_op
