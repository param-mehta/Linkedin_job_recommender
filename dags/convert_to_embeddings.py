from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain.embeddings import HuggingFaceInstructEmbeddings
import pymongo
from user_definition import *
import certifi
import warnings


def embed_descriptions():
    """
    This function embeds job descriptions using the specified Hugging Face model,
    connects to MongoDB to store the embeddings, and deletes existing embeddings.
    """
    # Suppress UserWarning from MongoDB deprecated TypedStorage
    warnings.filterwarnings('ignore', category=UserWarning, message='TypedStorage is deprecated')

    # Initialize Hugging Face embeddings
    embeddings_function = HuggingFaceInstructEmbeddings(
        model_name="hkunlp/instructor-base", model_kwargs={"device": 'cpu'}
    )

    # Establish MongoDB connection
    ca = certifi.where()
    client = pymongo.MongoClient(ATLAS_CONNECTION_STRING, tlsCAFile=ca)

    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    # Access MongoDB collections
    collection = client[DB_NAME][COLLECTION_NAME]
    new_jobs = collection.find()

    embeddings_collection = client[DB_NAME][JOBS_COLLECTION_NAME]
    embeddings_collection.delete_many({})

    # Embed each job description and store in MongoDB
    for job in new_jobs:
        descriptions = [job['clean_description']]
        metadatas = [job]
        vector_search = MongoDBAtlasVectorSearch.from_texts(
            descriptions,
            embeddings_function,
            metadatas,
            embeddings_collection
        )
        break

    for job in new_jobs:
        descriptions = [job['clean_description']]
        metadatas = [job]
        ids = vector_search.add_texts(descriptions, metadatas)

    print('Documents embedded successfully!')


if __name__ == "__main__":
    embed_descriptions()
