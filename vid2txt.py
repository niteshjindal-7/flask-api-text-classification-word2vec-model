import moviepy.editor as mp #video editing module
import os
import glob  
import pydub
from pydub import AudioSegment  #audio compression and remove disturbances from the audio file
import subprocess
import azure.storage.blob
#from azure.storage.blob import BlockBlobService, PublicAccess  # The Azure Storage Blobs client library for Python. Provide code chunks to interact with the the API
#import azure.cognitiveservices.speech as speechsdk
import time
import requests #make requests to azure speech to text rest api
import logging
import json
import natsort
from azure.storage.blob import PublicAccess
from pydub import AudioSegment
import math
from pydub.silence import split_on_silence
import speech_recognition as sr
#from multiprocessing import Pool
import pandas as pd
import csv

#os.cpu_count()

base_path="/home/nitesh/Documents/AMPBA/AISPRY/"
video_dir = '/home/nitesh/Documents/AMPBA/AISPRY/Video_Lectures_mp4'
audio_dir = "/home/nitesh/Documents/AMPBA/AISPRY/Audio_Files/"
procd_audio_dir = "/home/nitesh/Documents/AMPBA/AISPRY/Processed_Audio_Files/"
splitted_audio_dir = "/home/nitesh/Documents/AMPBA/AISPRY/Splitted_Audio_Files/"
text_dir = "/home/nitesh/Documents/AMPBA/AISPRY/Text_Files/"

os.getcwd()

########################VIDEO TO AUDIO ##x###################################

#video to audio and save them in a directory 
for file in os.listdir(video_dir):
    os.rename(os.path.join(video_dir, file), os.path.join(video_dir, file).replace(' ', '_')) 

for file in os.listdir(video_dir):
    if file.endswith('.mp4'):
        print(file)
        name=file
        clip = mp.VideoFileClip(video_dir + "/" + name)
        f, extension = os.path.splitext(file)
        clip.audio.write_audiofile(audio_dir + f +".wav")


#remove disturbances from the audion file by invoke SoX and save them in a different directory
for file in os.listdir(audio_dir):
    file_path= str(audio_dir + file)
    newfile_path= str(procd_audio_dir + file)
    print(file_path)
    print(newfile_path)
    subprocess.call(f"sox {file_path} -c 1 -r 16000 {newfile_path}", shell=True)


###################### SPLIT AUDIO FILES INTO AUDIO CHUNKS ###################


# split audio files and #remove_silence_from_audio(procd_audio_dir, splitted_audio_dir, file)

from_dir =  procd_audio_dir
to_dir = splitted_audio_dir
#file="Lecture_18__Bayesian_Learning.wav"
def remove_silence_from_audio(from_dir, to_dir, file):
    sound = AudioSegment.from_file(from_dir + file, format = "wav")
    audio_chunks = split_on_silence(sound, min_silence_len = 1500, silence_thresh = -45, keep_silence = 50)
    print("Audio Chunks Created")
    for i, chunk in enumerate(audio_chunks):
        print(i)
        os.makedirs(to_dir + file.split(".")[0], exist_ok=True)
        split_fn = to_dir + file.split(".")[0] + "/" + str(i) + "_" + file
        output_file=split_fn
        print("Exporting file", output_file)
        chunk.export(output_file, format="wav")

audio_files=os.listdir(procd_audio_dir)
list(map(lambda f: remove_silence_from_audio(procd_audio_dir , splitted_audio_dir, f) , audio_files)) 


'''We will see below two approaches that will convert the audio speech to text'''

################### Approach 1: USE AZURE SPEECH TO TEXT REST API##############################

# use azure speech to text rest api for chunked/short audio files:

speech_account_name="myspeechtotextaccount"
SPEECH_KEY= "3efe3c06fbf4408db59b2340ce352d3a"
SPEECH_KEY1="ba99b392673440ada87ee3263c626014"
SERVICE_REGION="centralindia"
ENDPOINT="https://centralindia.api.cognitive.microsoft.com/sts/v1.0/issuetoken"

subscription_key = SPEECH_KEY

'''get token which will be used to invoke the speech services. 
token would be valid for 10 mins only - '''

def get_token(subscription_key):
    fetch_token_url = 'https://centralindia.api.cognitive.microsoft.com/sts/v1.0/issuetoken'
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key   #unique to services on Azure platform
    }
    response = requests.post(fetch_token_url, headers=headers)
    access_token = str(response.text)
    return access_token

access_token=get_token(subscription_key)


''' The endpoint for the REST API for short audio has the below url
format and append the language parameter to the URL to avoid 
receiving a 4xx HTTP error - '''

url = "https://centralindia.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=en-US"


'''we can either use [Access_token] or the 
[subscription key/speech key] to invoke to speech services- '''

headers = {
  'Content-type': 'audio/wav;codec="audio/pcm";',
  'Authorization' : 'Bearer {}'.format(access_token)
#   'Ocp-Apim-Subscription-Key': subscription_key ,
}

# headers = {
#   'Content-type': 'audio/wav;codec="audio/pcm";',
#   'Ocp-Apim-Subscription-Key': subscription_key ,
    
# }

labels= os.listdir(splitted_audio_dir) #labels as folder names in chunked audio directory

labels_path=[os.path.join(splitted_audio_dir + label) for label in labels] #path pointing to each file in each folder in the audio chunks directory

response_labels= []
response_text=[]
for lp in labels_path[0:len(labels)]:
    for file in natsort.natsorted(os.listdir(lp)):
        print("\nFile name:{}\n".format(file))
        if file.endswith(".wav"):
            print(file)
            with open(lp + "/" + file,'rb') as payload:
                    response = requests.request("POST", url, headers=headers, data=payload)
                    #print(response)
            
                    try:
                        #diction =response.text
                        diction =json.loads(response.text) # json to python dictionary format 
                        print(diction)
                        if diction.get(("RecognitionStatus")) == 'InitialSilenceTimeout':
                            print("Pass")
                        else:
                            print("Execute")
                            #text_dict[lp] = str(diction.get("DisplayText"))
                            response_labels.append(str(lp))
                            response_text.append(str(diction.get(("DisplayText"))))
                            #response_text.append(response.text)
                            #print(str(diction.get(("DisplayText"))))
                
                    except json.decoder.JSONDecodeError as error:
                        print(error)



df=pd.DataFrame(zip(response_labels, response_text), columns= ['labels', 'content'])
df.to_csv('audiocontent.csv')


################### Approach 2: AUDIO TO TEXT USING GOOGLE SPEECH API IN PYTHON ######################

import speech_recognition as sr
labels= os.listdir(splitted_audio_dir) #labels as folder names in chunked audio directory
labels_path=[os.path.join(splitted_audio_dir + label) for label in labels] #path of each folder in the audio chunks directory

def recognize_text_from_short_audio(labelpath, filename):
    print("\nFile name:{}\n".format(filename))
    audiopath= labelpath+ "/" + filename
    r = sr.Recognizer()
    with sr.WavFile(audiopath) as source:  #sr.AudioFile
         try:

            audio_data = r.record(source) 
            ## listen for the data (load audio to memory)

            # recognize (convert from speech to text)
            text = r.recognize_google(audio_data)
            # #print(text)
            # response_text.append(text)
            # response_labels.append(filename)
            print(filename + " transcribed to text successfully")

         except sr.UnknownValueError:
            text= ""
            print("Could not understand audio")
            # response_text.append('')
            # response_labels.append(filename)
    return text
    

# response_text_fin= []
# response_labels_fin=[]


for label, lp in zip(labels[0:20],labels_path[0:20]):
    files= natsort.natsorted(os.listdir(lp))
    response_text1=list(map(lambda file_name: recognize_text_from_short_audio(lp, file_name) , files)) 
    response_labels1=files
    df= pd.DataFrame(zip(response_text1,response_labels1), columns=["content", "topics"])
    with open(text_dir + label + ".csv" ,'w') as f:
        df.to_csv(f)
        
    
###############################################################################################