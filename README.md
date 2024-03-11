# Linkedin Job Recommender

## Overview

An end-to-end job recommender engine that performs a similarity search between job descriptions and the uploaded resume to return the top 5 most relevant jobs

## Features

- Use Airflow to orchestrate data ingestion and preprocessing
  
    - Scrape thousands of job details daily for desired parameters such as job title and location, storing the JSON files on Google Cloud Storage.
    - Cleanse and preprocess raw data in parallel using PySpark, generating summary statistics about collected jobs using Spark SQL.
    - Convert job descriptions into word embeddings using Langchain.
    - Store job data and statistics as MongoDB collections.


- Develop a dashboard to display job statistics and recommend relevant jobs

    - Parse the user's resume using Google's Cloud Vision API and convert it into embeddings using Langchain.
    - Filter jobs from the database based on the parameters selected by the user.
    - Conduct similarity search between the resume text and job descriptions of filtered positions.
    - Display the details of the top k relevant jobs along with an LLM-generated summary explaining why the job description and resume constitute a suitable match.

 
## Pipeline Overview
<img width="1423" alt="Screenshot 2024-03-10 at 12 27 38 AM" src="https://github.com/param-mehta/Linkedin_job_recommender/assets/61198990/fd219f8e-5f01-4809-bd7a-b8e19c3e58de">

- The top branch of the pipeline is automated through Airflow. We scrape jobs from LinkedIn, clean data, calculate job statistics, convert descriptions to embeddings, and store processed data as MongoDB collections. Using a NoSQL database is advantageous because the data is ingested from multiple sources with different schemas and formats. Additionally, MongoDB's Atlas Vector Search allows storing vector embeddings alongside source data and provides efficient vector operations. While traditional SQL databases are fast on smaller datasets, vector databases scale better.

- The bottom branch of the pipeline represents the frontend. If you prefer not to have a live dashboard and want recommendations generated as part of the batch job, a minor tweak in the DAG pipeline suffices. Store your resume and add an additional task at the end of the DAG pipeline, which performs the similarity search and uses an EmailOperator to send you job URLs of top recommendations.

## DAG Workflow
<img width="1406" alt="image" src="https://github.com/param-mehta/Linkedin_job_recommender/assets/61198990/d5212a83-65b9-4610-a957-ca24660c4d22">


This is the top branch of the pipeline represented as a DAG diagram. It consists of four major tasks that run sequentially.

The following illustrates a cycle of successful DAG runs on Cloud Composer.


<img width="1468" alt="successful_airflow_run" src="https://github.com/param-mehta/Linkedin_job_recommender/assets/61198990/97d1085b-e5dc-476c-bc5d-978b40506bbf">



The `convert_to_embeddings` task takes longer because I am pushing individual jobs to the MongoDB collection rather than using a single push operation for all jobs, which would exceed the default memory limit of small Composer environments.



## Demo
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/xM8NA1D05hk/0.jpg)](https://www.youtube.com/watch?v=xM8NA1D05hk)


## Installation and Usage

#### Google Cloud Composer

To set up on Composer, create a Composer 2 Environment with a Medium size.

1. Configure the following environment variables in the Composer environment:
   ```bash
    #!/bin/bash
    export GS_BUCKET_NAME=""
    export GCP_PROJECT_NAME=""
    export MONGO_USERNAME=""
    export MONGO_PASSWORD=""
    export DB_NAME=""
    export ATLAS_CONNECTION_STRING="mongodb+srv://<user>:<password>@<database_name>.vnw63oa.mongodb.net/?retryWrites=true&w=majority"
    export VECTOR_INDEX_NAME=""
    export COLLECTION_NAME=""
    export JOBS_COLLECTION_NAME=""
    export COLLECTION_NAME_STATS=""
    export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
    ```
2. Install the following dependencies under the PyPI Packages tab in your Composer environment:
    ```bash
    google-cloud-aiplatform
    apache-airflow-providers-apache-spark
    pymongo[srv]==3.11
    langchain==0.1.5
    langchain-community==0.0.18
    langchain-google-vertexai==0.0.2
    InstructorEmbedding==1.0.1
    google-cloud-storage
    pyspark==3.4.1
    certifi
    torch==2.0.1
    sentence_transformers==2.2.22
    ```

#### Local

1. Set up an environment:
    ```bash
    conda create --name job_recommender python=3.11.7
    ```
    ```bash
    conda activate job_recommender
    ```
    ```bash
    bash env.sh
    source env.sh
    ```

2. Clone the repository and install dependencies:
    ```bash
    git clone https://github.com/yourusername/Linkedin_job_recommender.git
    ```
    ```bash
    cd Linkedin_job_recommender
    ```
    ```bash
    pip install -r requirements.txt
    ```

3. Initialize metastore:
    ```bash
    airflow db init
    ```

4. Create a DAG folder:
    ```bash
    mkdir ~/airflow/dags
    ```
    This directory should contain all your DAG files.

5. Start the scheduler to trigger the scheduled DAG runs:
    ```bash
    airflow scheduler
    ```

6. Run the webserver to monitor your DAG runs:
    ```bash
    airflow webserver
    ```

7. Launch the dashboard, upload your resume, and explore recommended jobs:
    ```bash
    streamlit run app.py
    ```

## Guide

`linkedin_dag.py`:

This is the main DAG file defining operators and dependencies, running daily.

`get_jobs_from_api.py`:

- Fetches data from LinkedIn using Jsearch API parameters.
- Stores JSON files in a GCS bucket.

`gcs_to_mongo.py`:

- Reads JSON files from the GCS bucket and converts them into a Spark RDD.
- Filters and modifies specific fields based on the desired format.
- Applies text cleaning functions to the job description field.
- Stores job details as a collection on a MongoDB Atlas cluster.

`convert_to_embeddings.py`:

Converts the description field into embeddings using Langchain, utilizing Instructor Embeddings from Hugging Face.

`calculate_summary_statistics.py`:

Converts the description field into embeddings using Langchain, utilizing Instructor Embeddings from Hugging Face.

`app.py`:

This Streamlit dashboard:
- Displays job statistics about collected jobs.
- Prompts the user to select search parameters and upload a resume.
- Parses resume text, embeds it, and performs similarity search to recommend top job positions.
- For each job, displays details like salary, location, URL, and similarity score.
- Also presents a Gemini-induced summary explaining why the resume is a good match for the selected job.

`helper.py`:

Contains helper functions used by `app.py`.

`user_definition.py`: 

Configuration file for importing environment variables.

## Time to find a job!
