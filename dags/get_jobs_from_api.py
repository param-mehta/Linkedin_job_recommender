import requests
import json
from datetime import datetime
import time
from google.cloud import storage
from google.oauth2 import service_account
from google.cloud import aiplatform
from user_definition import GOOGLE_API_STRING, GS_BUCKET_NAME


def write_data_to_gcs(bucket_name: str, folder_prefix: str, destination_file_name: str, json_data: str) -> None:
    """
    Write JSON data to Google Cloud Storage.

    Args:
        bucket_name (str): The name of the GCS bucket.
        folder_prefix (str): The prefix for the folder where the data will be stored.
        destination_file_name (str): The name of the file where the data will be stored.
        json_data (str): The JSON data to be stored.

    Returns:
        None
    """
    try:
        credentials = service_account.Credentials.from_service_account_info(json.loads(GOOGLE_API_STRING.strip(), strict=False))
        storage_client = storage.Client(project=credentials.project_id, credentials=credentials)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(folder_prefix + destination_file_name)
        blob.upload_from_string(json_data, content_type='application/json')
        print('Data written to GCS successfully')
    except Exception as e:
        print(e)
        print('Failed to write data to GCS')


def fetch_jobs_data(search_title: str) -> None:
    """
    Fetch job data for a given search title and write it to Google Cloud Storage.

    Args:
        search_title (str): The title of the job to search for.

    Returns:
        None
    """
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": "<your-api-key",
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    querystring = {"query": f"{search_title} USA", "page": "1", "num_pages": "20", "date_posted": "month"}

    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
    except Exception as e:
        print(f"Request failed: {e}")
        return

    folder_prefix = f"{datetime.now().strftime('%Y-%m-%d')}/"
    search_title_formatted = search_title.replace(" ", "")
    destination_file_name = f"{search_title_formatted}.json"

    bucket_name = GS_BUCKET_NAME
    json_data = json.dumps(data['data'])

    write_data_to_gcs(bucket_name, folder_prefix, destination_file_name, json_data)
    print(f"Successfully searched jobs for {search_title}")


def get_data() -> None:
    """
    Fetch job data for multiple search titles.

    Returns:
        None
    """
    for search_title in ['Data Scientist', 'Data Analyst', 'Machine Learning Engineer']:
        time.sleep(5)
        fetch_jobs_data(search_title)


if __name__ == "__main__":
    get_data()
