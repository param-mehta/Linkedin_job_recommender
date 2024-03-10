# Linkedin Job Recommender

## Overview

This repository contains the code to implement an automated data pipenline that scraps latest jobs from Linkedin and performs a similarity search between job descriptions and the uploaded resume to return the top 5 most relevant jobs

## Features

- Use Airflow to orchestrate the data ingestion and preprocessing pipeline
  
    - Scrap thousands of job details every day for the desired parameters of job title, location, etc and store as json files on Google Cloud Storage
    - Clean and preprocess raw data in parallel using pyspark. Generate summary statistics about collected jobs using Spark SQL 
    - Store job data and statistics as MongoDB collections
    - Convert job descriptions into word embeddings using Langchain 
       
- A dashboard to display job statistics and recommend relevant jobs

    - Parse user's resume using Google's Cloud Vision API and convert into embeddings using Langchain
    - Filter jobs from database based on the parameters selected by user
    - Perform similarity search between resume text and job descriptions of filtered positions
    - Display the details of top k relevant jobs along with an LLM generated summary explaining why the job description and resume constitute a suitable match
<img width="1423" alt="Screenshot 2024-03-10 at 12 27 38 AM" src="https://github.com/param-mehta/Linkedin_job_recommender/assets/61198990/fd219f8e-5f01-4809-bd7a-b8e19c3e58de">


## Requirements

To run the trading strategy, you need to do the following:

- Get Zerodha Kite Connect API credentials from https://kite.trade/
- Enable TOTP verification in your kite account
- Install the dependencies as shown below

## Installation

1. Make an environment:

    ```bash
    conda create --name algo_trading python=3.11.7
    ```
    
    ```bash
    conda activate algo_trading
    ```
    
2. Clone the repository and install dependencies:
   
    ```bash
    cd algorithmic-trading-strategy
    ```
    
    ```bash
    git clone https://github.com/yourusername/Algo_trading_bot.git
    ```

    ```bash
    pip install -r requirements.txt
    ```


## Usage

1. Setup the environment following variables on Google Composer. If you are runnning locally, run `bash env.sh` to set environment variables.
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
2. Install the following dependencies under the PyPI Packages tab on Google Composer. If running locally, run `pip install -r requirements.txt`
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

6. Run `streamlit run app.py`, upload resume and check out recommended jobs!


## Guide

`linkedin_dds.py`: 

This contains helper functions to:
- Place and modify normal orders, stop loss orders or gtt orders
- Calculate technical indicators such as bollinger bands and Volume Weighted Average Price
- Fetch historical data and perform error handling

While the helper functions are using the Kite Connect's python client, the main strategy code has been written in a way that one can switch to another platform's API with minimal changes.

`get_jobs_from_api.py`:

This script initializes the data structures and files needed to store trade details and trading parameters relevant to the strategy. 

`gcs_to_mongo.py`:

This script initializes the data structures and files needed to store trade details and trading parameters relevant to the strategy. 

`convert_to_embeddings.py`:

This script uses Selenium to automate the process of logging into the account of kite and fetching the access_tokens for multiple accounts.

`app.py`:

This script fetches daily instrument data and initializes files to store trade details and strategy paramters for a single trading session

`helper.py`:

This script contains the main strategy loop that checks conditions, executes trades and updates the trailing stop loss. The script stops running when either the max no. of cycles is reached or when the trading session concludes. 

`user_definition.py`: 

This contains a simple streamlit dashboard that displays the open positions, completed orders, failer orders and runtime errors.

