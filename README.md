# Linkedin Job Recommender

## Overview

An end-to-end job recommender engine that performs a similarity search between job descriptions and the uploaded resume to return the top 5 most relevant jobs

## Features

- Use Airflow to orchestrate data ingestion and preprocessing
  
    - Scrap thousands of job details every day for the desired parameters of job title, location, etc and store the json files on Google Cloud Storage
    - Clean and preprocess raw data in parallel using pyspark. Generate summary statistics about collected jobs using Spark SQL 
    - Store job data and statistics as MongoDB collections
    - Convert job descriptions into word embeddings using Langchain 
       
- A dashboard to display job statistics and recommend relevant jobs

    - Parse user's resume using Google's Cloud Vision API and convert into embeddings using Langchain
    - Filter jobs from database based on the parameters selected by user
    - Perform similarity search between resume text and job descriptions of filtered positions
    - Display the details of top k relevant jobs along with an LLM generated summary explaining why the job description and resume constitute a suitable match.
 
## Pipeline Overview
<img width="1423" alt="Screenshot 2024-03-10 at 12 27 38 AM" src="https://github.com/param-mehta/Linkedin_job_recommender/assets/61198990/fd219f8e-5f01-4809-bd7a-b8e19c3e58de">

- The top branch of the pipeline is what we automate through Airflow. We scrap jobs from LinkedIn, clean data, calculate job statistics,convert descriptions to embeddings and store processed data as MongoDB collections. The reason I am using a NoSQl database is because the data is ingested from multiple sources with different schema and format. Also, MongoDB's Atlas Vector Search allows you to store vector embeddings alongside your source data and provides efficient vector operations on these embeddings. While tradiotional SQL databases are sufficiently fast on data that's not too large, vector databases scale much better than the former.

- The bottom branch of the pipline represents the front end. If you don't want a live dashboard and want the recommendations to be generated as part of the batch job, you can make a minor tweak in the DAG pipeline. Store your resume and add an additional task at the end of the DAG pipeline which performs the similarity search and uses an EmailOperator to send you job urls of top recommendations.

## DAG Workflow
<img width="1406" alt="image" src="https://github.com/param-mehta/Linkedin_job_recommender/assets/61198990/d5212a83-65b9-4610-a957-ca24660c4d22">


This is what the top branch of the pipeline looks like as a DAG diagram. There are 4 major tasks that run sequentially


This following is what a cycle of successful DAG runs looks like on Cloud Composer


<img width="1468" alt="successful_airflow_run" src="https://github.com/param-mehta/Linkedin_job_recommender/assets/61198990/97d1085b-e5dc-476c-bc5d-978b40506bbf">



The `convert_to_embeddings` task takes long because I am pushing individual jobs to the MongoDB collection rather than an a single push operation of all jobs that would end up overshooting the default memory (1GB) of small Composer environments


## Demo
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/xM8NA1D05hk/0.jpg)](https://www.youtube.com/watch?v=xM8NA1D05hk)



## Installation and Usage

### Google Cloud Composer

On composer, you need to create a Composer 2 Environment with size Medium.

1. Setup the following environment variables in the Composer environment.
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
2. Install the following dependencies under the PyPI Packages tab on in your Composer environment.
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


### Local


1. Make an environment:

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
3. Initialise metastore:
    ```bash
    airflow db init
    ```
4. Make a DAG folder:
    ```bash
    mkdir ~/airflow/dags
    ```
    This is where all your dag files should be

5. Run the scheduler to trigger the scheduled dag runs:
    ```bash
    airflow scheduler
    ```
6. Run the webserver to monitor your dag runs:
    ```bash
    airflow webserver
    ```
7. Start the dashboard, upload resume and check out recommended jobs!
    ```bash
    streamlit run app.py
    ```


## Guide

`linkedin_dag.py`: 

This is the main DAG file that defines all the operators and the dependencies between them. It runs on a daily basis.

`get_jobs_from_api.py`:

- fetches data from Linkedin using the provided parameters through the Jsearch API
- stores the json files in GCS bucket. 

`gcs_to_mongo.py`:

- reads json files from GCS bucket and converts them into a spark rdd
- filters and modifies specific fields based on the desired format
- Applies text cleaning functions on the job description field.
- Stores the job details as a collection on a MongoDB Atlas cluster

`convert_to_embeddings.py`:

This script converts the description field into embeddings using Langchain. It uses Instructor Embeddings from Hugging Face

`calculate summary_statistics.py`:

This script converts the description field into embeddings using Langchain. It uses Instructor Embeddings from Hugging Face

`app.py`:

This script is a streamlit dashboard that 

- displays the job statistics about the collected jobs
- Prompts the user to select search parameters and upload the resume
- Parses resume text, embeds it and performs similarity search to recommend top k job positions
- For each job, displays job details like salary, location, url and similarity score
- Also displays a Gemini induced summary explaining why the resume is a good match for the selected job

`helper.py`:

This script contains the helper functions used by app.py.

`user_definition.py`: 

Configuration file to import environment variables.


## Time to find a job!
