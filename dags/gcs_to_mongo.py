import os
import json
import pymongo
from google.cloud import storage
from google.cloud import aiplatform
from pyspark.sql import SparkSession
from google.oauth2 import service_account
import certifi
import nltk
import re
from datetime import datetime
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from user_definition import *

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
stop_words = set(stopwords.words('english'))

json_creds = json.loads(GOOGLE_API_STRING.strip(), strict=False)
project_id = json_creds['project_id']
credentials = service_account.Credentials.from_service_account_info(json_creds)
aiplatform.init(project=project_id, credentials=credentials)


def clean_text(text):
    """
    Cleans and preprocesses text data.

    Args:
        text (str): Input text to be cleaned.

    Returns:
        str: Cleaned text.
    """
    # Lowercasing
    text = text.lower()
    # Remove special characters, numbers, and punctuations
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Tokenization
    words = word_tokenize(text)
    # Remove stopwords
    words = [word for word in words if word not in stop_words]
    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]
    # Join the words back into a string
    clean_text = ' '.join(words)
    return clean_text


def clean_job_data_spark(df, searchTitle):
    """
    Cleans job data using Spark DataFrame.

    Args:
        df (DataFrame): Input DataFrame containing job data.
        searchTitle (str): Search title for the job.

    Returns:
        RDD: Cleaned job data RDD.
    """
    def clean_job(row):
        job = row.asDict()
        # Skipping jobs with missing fields
        if job['job_description'].strip() == '' \
                or job['job_title'].strip() == '' \
                or job['job_apply_link'].strip() == '' \
                or job['employer_name'].strip() == '':
            return None

        # Combining location fields into one
        location_parts = [job['job_city'], job['job_state'], job['job_country']]
        job['location'] = ' - '.join(filter(None, location_parts))

        # Combining salary fields into one
        salary_parts = [str(job['job_min_salary']), str(job['job_max_salary'])]
        job['salary'] = ' - '.join(filter(None, salary_parts))

        desired_field_names = ['id', 'companyName', 'title', 'salary',
                               'jobUrl', 'location', 'postedTime', 'description']
        original_field_names = ['job_id', 'employer_name', 'job_title', 'salary',
                                'job_apply_link', 'location', 'job_posted_at_datetime_utc', 'job_description']

        # Standardizing field names across different APIs
        for key1, key2 in zip(desired_field_names, original_field_names):
            job[key1] = job[key2]

        # Removing unwanted fields and adding searchTitle
        cleaned_job = {key: job[key] for key in desired_field_names if key in job}
        cleaned_job['searchTitle'] = searchTitle

        # cleaning description column
        cleaned_job['clean_description'] = clean_text(cleaned_job['description'])
        return cleaned_job

    cleaned_jobs_rdd = df.rdd.map(clean_job).filter(lambda x: x is not None)
    return cleaned_jobs_rdd


def clean_data(spark, bucket_name, blob_name, searchTitle):
    """
    Cleans data from GCS and creates RDD.

    Args:
        spark (SparkSession): Spark session.
        bucket_name (str): GCS bucket name.
        blob_name (str): Blob name.
        searchTitle (str): Search title for the job.

    Returns:
        RDD: Cleaned job data RDD.
    """
    # Read JSON file from Google Cloud Storage
    gcs_path = f"gs://{bucket_name}/{blob_name}"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    with open("/tmp/temp_file.json", "wb") as file:
        blob = bucket.blob(blob_name)
        blob.download_to_file(file)

    # Convert JSON file to Spark DataFrame
    df = spark.read.json("/tmp/temp_file.json")

    try:
        cleaned_jobs_rdd = clean_job_data_spark(df, searchTitle)
        print("Cleaned json data. RDD created successfully!")
        print(f"No of jobs to insert = {cleaned_jobs_rdd.count()}")
        return cleaned_jobs_rdd
    except Exception as e:
        print(e)


def push_to_mongo(mongo_collection, input_data):
    """
    Pushes RDD data into MongoDB.

    Args:
        mongo_collection: MongoDB collection to insert data into.
        input_data: RDD data to be inserted into MongoDB collection.

    Returns:
        None
    """
    try:
        mongo_collection.insert_many(input_data.collect(), ordered=False)
        print("Documents inserted to MongoDB successfully!")
    except Exception as e:
        print(e)
        print("Failed to insert documents to MongoDB!")


def gcs_to_mongodb_collection():
    """
    Transfers data from GCS to MongoDB collection after cleaning.

    This function cleans the data from GCS and inserts it into MongoDB.
    """
    # Initialize Spark session
    spark_session = SparkSession.builder.getOrCreate()
    conf = spark_session.sparkContext._jsc.hadoopConfiguration()
    conf.set(
        "google.cloud.auth.service.account.json",
        GOOGLE_API_STRING,
    )
    conf.set("fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
    conf.set(
        "fs.AbstractFileSystem.gs.impl",
        "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem",
    )

    # Set up MongoDB connection
    ca = certifi.where()
    client = pymongo.MongoClient(ATLAS_CONNECTION_STRING, tlsCAFile=ca)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Clean data and create RDD
    folder_prefix = f"{datetime.now().strftime('%Y-%m-%d')}/"
    collection.delete_many({})

    for searchTitle in ['Data Scientist', 'Data Analyst', 'Machine Learning Engineer']:
        blob_name = folder_prefix + searchTitle.replace(" ", "") + '.json'
        input_rdd = clean_data(spark_session, GS_BUCKET_NAME, blob_name, searchTitle)
        push_to_mongo(collection, input_rdd)

    spark_session.stop()


if __name__ == "__main__":
    gcs_to_mongodb_collection()
