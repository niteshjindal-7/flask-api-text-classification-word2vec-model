
import pandas as pd
import numpy as np
# pd.set_option('display.max_colwidth', -1)
import os
from utilityfunction import textpreprocess
from utilityfunction import LossLogger
from utilityfunction import MySentences
from utilityfunction import doc_vectors_from_wvs
from gensim.models import Word2Vec # runs Word2Vec model
from gensim.models import KeyedVectors
from sklearn.metrics.pairwise import cosine_similarity
import flask
from flask import request, jsonify
from flask import render_template
import subprocess # run command line function in python
import warnings # suppress warnings
import shutil # unzip files
import gdown
subprocess.run(['pip', 'install', 'gdown==4.2.0'])
warnings.filterwarnings("ignore")




#load text files from google drive
url = 'https://drive.google.com/uc?id=1ur93ZLBLGWPzvDDnxzHuThCYCofp5wOK'
output = 'Text_Files.zip'
gdown.download(url, output, quiet=False, verify=False)
shutil.unpack_archive('Text_Files.zip', 'Text_Files')


#load trained word embedding model from google drive
url = 'https://drive.google.com/uc?id=1pnRT9we46ex4KO-my1DyjhIMHodS1gHd'
output = 'WordEmbeddings.zip'
gdown.download(url, output, quiet=False, verify=False)
shutil.unpack_archive('WordEmbeddings.zip', 'WordEmbeddings')



#####refer the vid2txt.py for speech to text conversion.
text_dir = os.getcwd() + "/Text_Files/Text_Files/"
# preprocess_dir= "/home/nitesh/Documents/AMPBA/AISPRY/Preprocessed_Files/"
wordembedding_dir = os.getcwd() + "/WordEmbeddings/WordEmbeddings/"


#####text files 
files = []
fnames = os.listdir(text_dir)
for name in fnames:
    if name.endswith('.csv'):
        files.append(name)

#####text corpus (list of list of n-grams)
l=list(map(lambda f: textpreprocess(f, text_dir=text_dir), files)) 


K=5
content= list(map(lambda f: str(list(f.values())).split(),l)) # split sentences to tokens
corpus=list(map(lambda con: con[K: len(con) - K], content)) # remove first and last 5 words from the text as they contain headers and are not informative


embeddingsize = 70
win_size =  5
model1 = KeyedVectors.load(wordembedding_dir + "wordembeddingmodel" + str(embeddingsize) + '_' + str(win_size), mmap='r')
model_vocab = model1.wv.index_to_key #list of model vocabulary words

vector_dct = {}
for word in model_vocab:  # changes to kv_model.index_to_key in gensim-4.0.0
    vector_dct[word] = model1.wv.get_vector(word)

word_vectors_matrix = pd.DataFrame(vector_dct).T


#####create document embeddings corresponding to each topic or list of strings in corpus
doc_vecs=list(map(lambda list_of_words: doc_vectors_from_wvs(word_vectors_matrix , list_of_words), corpus))

labels= files
doc_vecs_dict= {}
for lbl, d in zip(labels, doc_vecs):
    doc_vecs_dict[lbl] = d

doc_vecs_df=pd.DataFrame(doc_vecs_dict) #contains averaged embedding  each document.

#check similarity score for a new example and assign the example to a particular label/topic 


#####test model



app = flask.Flask(__name__) #create application instance 
app.config["DEBUG"] = True


# @app.route('/homepage')
# def homepage():
#     return HOME_HTML

     
# HOME_HTML = """
#      <html><body>
#          <h2>Welcome to the Query Page</h2>
#          <form action="/viewoutput">
#              Enter the query to find the respective taught module? <input type='text' name='inputquery'>><br>
#              <input type='submit' value='Continue'>
#          </form>
#      </body></html>"""


@app.route('/homepage')
def hello(name=None):
    return render_template('hello_html.html')


@app.route('/viewoutput', methods=['GET']) # Use the route() decorator to bind a function to a URL.
def viewoutput():
    val= request.args.get('inputquery', ' ')
    # val = input("Enter string: ") 
    keywords = val.split()
    testwords = [word for word in keywords if word in model_vocab]
    testwords_meanvec = np.mean(model1.wv[testwords], axis=0)
    testwords_meanvec1 = testwords_meanvec.reshape(1,embeddingsize)
    te=cosine_similarity(doc_vecs_df.T.values, testwords_meanvec1).reshape(len(labels),)
    cosine_sim_matrix = pd.DataFrame(zip(labels,te))
    cosine_sim_matrix.columns=['topic','sim_score']
    otpt=cosine_sim_matrix.nlargest(3,'sim_score') # this output , we want to display using flask api
    # otpt=otpt.to_json()
    otpt_dict= {}
    for lbl, d in zip(otpt.topic, otpt.sim_score):
        otpt_dict[lbl] = d
    return jsonify(otpt_dict)
    # return jsonify(otpt)

app.run(debug=False)




# val = input("Enter string: ") 
# "standard deviation for normal distribution calculation"
# keywords = val.split()
# testwords = [word for word in keywords if word in model_vocab]
# testwords_meanvec = np.mean(model1.wv[testwords], axis=0)
# testwords_meanvec1 = testwords_meanvec.reshape(1,embeddingsize)


# te=cosine_similarity(doc_vecs_df.T.values, testwords_meanvec1).reshape(len(labels),)
# cosine_sim_matrix = pd.DataFrame(zip(labels,te))
# cosine_sim_matrix.columns=['topic','sim_score']
# output=cosine_sim_matrix.nlargest(3,'sim_score') # this output , we want to display using flask api



# output_dict= {}
# for lbl, d in zip(output.topic, output.sim_score):
#     output_dict[lbl] = d