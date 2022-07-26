
import os
import azure.storage.blob
#from azure.storage.blob import BlockBlobService, PublicAccess  # The Azure Storage Blobs client library for Python. Provide code chunks to interact with the the API
from azure.storage.blob import BlobServiceClient



base_path="/home/nitesh/Documents/AMPBA/AISPRY/"
video_dir = '/home/nitesh/Documents/AMPBA/AISPRY/Video_Lectures_mp4'
audio_dir = "/home/nitesh/Documents/AMPBA/AISPRY/Audio_Files/"
procd_audio_dir = "/home/nitesh/Documents/AMPBA/AISPRY/Processed_Audio_Files/"
splitted_audio_dir = "/home/nitesh/Documents/AMPBA/AISPRY/Splitted_Audio_Files/"
text_dir = "/home/nitesh/Documents/AMPBA/AISPRY/Text_Files/"


#################Use Azure Storage Blob Service to host the audio files############

account_name='myaudiostorageaccount'
account_key='zsOb5yGO0/pLa61E/DM/XXXXXXXXXXXXXXXXXXXX/im+Ng3TP3u6m1Wi6nJH+AStZxn6Wg=='
# block_blob_service=BlockBlobService(account_name=account_name, account_key=account_key)
container_name='myresourcegroup'

# SERVICE_REGION = "Central India"
# NAME = "S2T"
# DESCRIPTION = "Speech to text"
# LOCALE = "en-GB"

#export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=myaudiostorageaccount;AccountKey=zsOb5yGO0/pLa61E/DM/Hmd1aGttlkO7PQOadyS+bO9ABgOoV589HdIy/im+Ng3TP3u6m1Wi6nJH+AStZxn6Wg==;EndpointSuffix=core.windows.net"
connect_str=os.environ.get("AZURE_STORAGE_CONNECTION_STRING")  # get the connection string from global environment variables. connection string corresponding to access key 1 of azure blob storage account


#Interaction with storage accounts, blob storage containers starts with an instance of a client (i.e. object of client). 
#Create client object-
service = BlobServiceClient(account_url="https://myaudiostorageaccount.blob.core.windows.net/", credential=account_key)
 ## service = BlobServiceClient.from_connection_string(conn_str=connect_str)

#create container-
service.create_container(container_name)


#upload blobs to container-
audio_file= "Lecture_03__Hypothesis_Space_and_Inductive_Bias.wav"

blob_client = service.get_blob_client(container_name, audio_file)

print("\nUploading to Azure Storage as blob:\n\t" + audio_file)
upload_file_path = os.path.join(procd_audio_dir, audio_file)

with open(upload_file_path, "rb") as data:
    blob_client.upload_blob(data)
