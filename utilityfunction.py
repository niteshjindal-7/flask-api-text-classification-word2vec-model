import pandas as pd
import numpy as np # used for averaging the embedding vectors
pd.set_option('display.max_colwidth', -1)
import re
import os
import nltk.corpus
nltk.download('stopwords')
from nltk.corpus import stopwords
stop_words = stopwords.words('english')
import logging
import sys
import requests
import time
import swagger_client as cris_client
from gensim.models.callbacks import CallbackAny2Vec
import logging
from gensim.models import phrases



###################speech to text service when video resides on azure storage blob.##################

speech_account_name="myspeechtotextaccount"
SPEECH_KEY= "3efe3c06fbf4408db59b2340ce352d3a"
SPEECH_KEY1="ba99b392673440ada87ee3263c626014"
SERVICE_REGION="centralindia"
ENDPOINT="https://centralindia.api.cognitive.microsoft.com/sts/v1.0/issuetoken"

#generate blob sas token and url
blob_sas_token='sp=r&st=2022-07-10T08:55:33Z&se=2022-07-10T16:55:33Z&spr=https&sv=2021-06-08&sr=b&sig=CHP7kBvXcDnmzhG%2Fca6sTYzmbRTBvPZ4LDBguGp6kgw%3D'
blob_sas_url="https://myaudiostorageaccount.blob.core.windows.net/myresourcegroup/Lecture_03__Hypothesis_Space_and_Inductive_Bias.wav?sp=r&st=2022-07-10T08:55:33Z&se=2022-07-10T16:55:33Z&spr=https&sv=2021-06-08&sr=b&sig=CHP7kBvXcDnmzhG%2Fca6sTYzmbRTBvPZ4LDBguGp6kgw%3D"

#we will interact with the speech rest api v3.0 using swagger client. to generate swagger client, we would use the swagger document format of azure speech to text api.
s2t_swagger_url="https://centralindia.dev.cognitive.microsoft.com/docs/services/speech-to-text-api-v3-0/export?DocumentFormat=Swagger&ApiName=Speech%20to%20Text%20API%20v3.0"

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
        format="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p %Z")

# Your subscription key and region for the speech service
SUBSCRIPTION_KEY = "3efe3c06fbf4408db59b2340ce352d3a"
SERVICE_REGION = "centralindia"
# SERVICE_REGION = "westus"
NAME = "S2T"
DESCRIPTION = "SpeechtoText"

LOCALE = "en-US"
RECORDINGS_BLOB_URI = blob_sas_url

# Provide the uri of a container with audio files for transcribing all of them
# with a single request. At least 'read' and 'list' (rl) permissions are required.
RECORDINGS_CONTAINER_URI = "<Your SAS Uri to a container of audio files>"

# Set model information when doing transcription with custom models
MODEL_REFERENCE = None  # guid of a custom model





def transcribe_from_single_blob(uri, properties):
    transcription_definition = cris_client.Transcription(
        display_name=NAME,
        description=DESCRIPTION,
        locale=LOCALE,
        content_urls=[uri],
        properties=properties
    )

    return transcription_definition


# def transcribe_with_custom_model(api, uri, properties):
#     """
#     Transcribe a single audio file located at `uri` using the settings specified in `properties`
#     using the base model for the specified locale.
#     """
#     # Model information (ADAPTED_ACOUSTIC_ID and ADAPTED_LANGUAGE_ID) must be set above.
#     if MODEL_REFERENCE is None:
#         logging.error("Custom model ids must be set when using custom models")
#         sys.exit()

#     model = api.get_model(MODEL_REFERENCE)

#     transcription_definition = cris_client.Transcription(
#         display_name=NAME,
#         description=DESCRIPTION,
#         locale=LOCALE,
#         content_urls=[uri],
#         model=model,
#         properties=properties
#     )

#     return transcription_definition


# def transcribe_from_container(uri, properties):
#     """
#     Transcribe all files in the container located at `uri` using the settings specified in `properties`
#     using the base model for the specified locale.
#     """
#     transcription_definition = cris_client.Transcription(
#         display_name=NAME,
#         description=DESCRIPTION,
#         locale=LOCALE,
#         content_container_url=uri,
#         properties=properties
#     )

#     return transcription_definition


def _paginate(api, paginated_object):
    """
    The autogenerated client does not support pagination. This function returns a generator over
    all items of the array that the paginated object `paginated_object` is part of.
    """
    yield from paginated_object.values
    typename = type(paginated_object).__name__
    auth_settings = ["apiKeyHeader", "apiKeyQuery"]
    while paginated_object.next_link:
        link = paginated_object.next_link[len(api.api_client.configuration.host):]
        paginated_object, status, headers = api.api_client.call_api(link, "GET",
            response_type=typename, auth_settings=auth_settings)

        if status == 200:
            yield from paginated_object.values
        else:
            raise Exception(f"could not receive paginated data: status {status}")


# def delete_all_transcriptions(api):
#     """
#     Delete all transcriptions associated with your speech resource.
#     """
#     logging.info("Deleting all existing completed transcriptions.")

#     # get all transcriptions for the subscription
#     transcriptions = list(_paginate(api, api.get_transcriptions()))

#     # Delete all pre-existing completed transcriptions.
#     # If transcriptions are still running or not started, they will not be deleted.
#     for transcription in transcriptions:
#         transcription_id = transcription._self.split('/')[-1]
#         logging.debug(f"Deleting transcription with id {transcription_id}")
#         try:
#             api.delete_transcription(transcription_id)
#         except cris_client.rest.ApiException as exc:
#             logging.error(f"Could not delete transcription {transcription_id}: {exc}")


def transcribe():
    logging.info("Starting transcription client...")

    # configure API key authorization: subscription_key
    configuration = cris_client.Configuration()
    configuration.api_key["Ocp-Apim-Subscription-Key"] = SUBSCRIPTION_KEY
    configuration.host = f"https://{SERVICE_REGION}.api.cognitive.microsoft.com/speechtotext/v3.0"
    # configuration.host = "https://{}.cris.ai".format(SERVICE_REGION)


    # create the client object and authenticate
    client = cris_client.ApiClient(configuration)

    # create an instance of the transcription api class
    # api = cris_client.DefaultApi(api_client=client)
    api = cris_client.CustomSpeechTranscriptionsApi(api_client=client)

    # Specify transcription properties by passing a dict to the properties parameter. See
    # https://docs.microsoft.com/azure/cognitive-services/speech-service/batch-transcription#configuration-properties
    # for supported parameters.
    properties = {
        # "punctuationMode": "DictatedAndAutomatic",
        # "profanityFilterMode": "Masked",
        # "wordLevelTimestampsEnabled": True,
        # "diarizationEnabled": True,
        # "destinationContainerUrl": "<SAS Uri with at least write (w) permissions for an Azure Storage blob container that results should be written to>",
        # "timeToLive": "PT1H"
    }

    # Use base models for transcription. Comment this block if you are using a custom model.
    transcription_definition = transcribe_from_single_blob(RECORDINGS_BLOB_URI, properties)

    # Uncomment this block to use custom models for transcription.
    # transcription_definition = transcribe_with_custom_model(api, RECORDINGS_BLOB_URI, properties)

    # Uncomment this block to transcribe all files from a container.
    # transcription_definition = transcribe_from_container(RECORDINGS_CONTAINER_URI, properties)

    created_transcription, status, headers = api.create_transcription_with_http_info(transcription=transcription_definition)

    # get the transcription Id from the location URI
    transcription_id = headers["location"].split("/")[-1]

    # Log information about the created transcription. If you should ask for support, please
    # include this information.
    logging.info(f"Created new transcription with id '{transcription_id}' in region {SERVICE_REGION}")

    logging.info("Checking status.")

    completed = False

    while not completed:
        # wait for 5 seconds before refreshing the transcription status
        time.sleep(5)

        transcription = api.get_transcription(transcription_id)
        logging.info(f"Transcriptions status: {transcription.status}")

        if transcription.status in ("Failed", "Succeeded"):
            completed = True

        if transcription.status == "Succeeded":
            pag_files = api.get_transcription_files(transcription_id)
            for file_data in _paginate(api, pag_files):
                if file_data.kind != "Transcription":
                    continue

                audiofilename = file_data.name
                results_url = file_data.links.content_url
                results = requests.get(results_url)
                logging.info(f"Results for {audiofilename}:\n{results.content.decode('utf-8')}")
        elif transcription.status == "Failed":
            logging.info(f"Transcription failed: {transcription.properties.error.message}")


if __name__ == "__main__":
    transcribe()



# function to remove urls,newline character, and non-essential words from text
def text_clean(temp: 'str'):
    text1 =pd.Series(temp)
    text11 = [string for string in text1 if string != ""]
    text1 = [re.sub('\S*@\S*\s?', '', sent) for sent in text11] # Remove emails
    text1 = [re.sub(r"http\S+", "", sent) for sent in text1] # remove urls
    text2 = [re.sub('\s+', ' ', sent) for sent in text1] # Remove newline character
    text3 = [re.sub("\'", "", sent) for sent in text2] # Remove distracting single quotes
    text4 = [re.sub('[^A-Za-z0-9]+', ' ', sent) for sent in text3] # remove alphanumeric values
    text5 = [''.join(i for i in s if not i.isdigit()) for s in text4] # remove numbers
    text5 = [s.strip() for s in text5]
    text5 = [l.lower() for l in text5]
    return text5



def textpreprocess(filename, text_dir: "str") -> "dict": 
    mydict={}
    print("Reading File "+str(filename))
    df1 = pd.read_csv(text_dir + filename, encoding= 'latin1') 
    #df1=pd.read_pickle(filename)#pathname + 
    #df1["text"] = df1["summary"] + "." + df1["description"] + "." + df1["resolution"]
    textdata1= str(df1.content)
    labelname=str(filename)
    #temp = []
    #for i in range(len(textdata1)):
        #temp += textdata1[i].split('.')
    text5 = text_clean(textdata1)  # call text_clean function
    corpus = [[word for word in doc.split()] for doc in text5] 
    corpus1 = [([i for i in doc if i not in stop_words]) for doc in corpus]
    corpus2 = [x for x in corpus1 if x]
    text5_1 =  [' '.join(i) for i in corpus2]
    mydict[filename] = text5_1
    # text6 = pd.DataFrame(text5_1, columns = ["text"])
    # text6.to_csv(preprocess_dir + filename, index= True)
    # #output_filename=filename.replace(pathname,output_pathname)
    #text6.to_pickle(output_pathname + output_filename)
    return mydict



#'convert tuple to string'
def convertTuple(tup):
    st = ''.join(map(str, tup))
    return st




#read list of list of strings as input in word2vec model
class MySentences():
    def __init__(self,input_file):
        self.input_file= input_file

    def __iter__(self):
        for file in self.input_file:
            yield file
        


#log the loss records and save word2vec model when threshold condition is met
class LossLogger(CallbackAny2Vec):
    
    def __init__(self, wordembedding_dirname, embeddingsize, win_size):  # mod_savepath
        self.epoch=0
        self.loss_init = 0
        #self.mod_savepath = mod_savepath  # to save output model
        # os.makedirs(self.wordembedding_dirname, exist_ok=True)
        self.wordembedding_dirname = wordembedding_dirname
        self.embeddingsize  = embeddingsize 
        self.win_size = win_size


        
    def on_epoch_end(self,model):
        '''
        Get the latest training loss, actual loss, and log the loss values in all epochs during model training
        
        '''
        loss=model.get_latest_training_loss()
        loss_actual = loss - self.loss_init # loss = cummulative loss; loss_init = cummulative loss till prev. step
        self.loss_init = loss  #initialise loss with cummulative value.
        
        print('\n\nCumm and Actual Loss after epoch {}: {} & {}\n\n'.format(self.epoch, self.loss_init, loss_actual))
    
        logging.info('\nLoss after epoch {}: {}\n\n'.format(self.epoch, loss))
        #logs = print(loss)
       
        with open(self.wordembedding_dirname  + "wordembeddinglossinfo" + str(self.embeddingsize) + '_' + str(self.win_size) + '.txt', "a") as myfile:
            myfile.write(str(self.epoch) + "," + str(loss) + "," + str(loss_actual) + "\n")
        

        threshold = (1*loss)/100
        wordembedding_path = self.wordembedding_dirname
        wordembedding_path = wordembedding_path + 'wordembeddingmodel' + str(self.embeddingsize) + '_' + str(self.win_size)  # changed
        if(loss_actual < threshold):
            model.save(wordembedding_path)
        else:
            logging.info('\n [[[Threshold {} > Actual Loss {} ]]] for epoch {} \n'. format(threshold,loss_actual, self.epoch))
    

           
            logging.info("Model saved for epoch"+ str(self.epoch))
            #logs.save(wordembedding_path + 'logs.txt')
            #print('Time taken in epoch run:', time.time() - start_time)
        
        self.epoch=self.epoch+1



#document vector from word vectors 
def doc_vectors_from_wvs(df, list_ngrams):
    '''
    #params: list of n-grams 
    #params: matrix words and their corresponding embeddings
    #output: numpy array of shape (embeddingsize,)
    '''
    arr=np.array(df[df.index.isin(list_ngrams)])
    doc_vec= np.mean(arr, axis=0)
    return doc_vec