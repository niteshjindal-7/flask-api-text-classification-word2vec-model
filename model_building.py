
import markdown
markdown.markdown('[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/niteshjindal170988/supervised-learning/blob/main/classification/decision-tree/decision-tree.ipynb)')


import pandas as pd
pd.set_option('display.max_colwidth', -1)
import os
from utilityfunction import textpreprocess
from gensim.models import Word2Vec # runs Word2Vec model
from utilityfunction import LossLogger
from utilityfunction import MySentences
import warnings
import subprocess
import gdown
import shutil
subprocess.run(['pip', 'install', 'gdown==4.2.0'])
warnings.filterwarnings("ignore")


#load text files from google drive
url = 'https://drive.google.com/uc?id=1ur93ZLBLGWPzvDDnxzHuThCYCofp5wOK'
output = 'Text_Files.zip'
gdown.download(url, output, quiet=False, verify=False)
shutil.unpack_archive('Text_Files.zip', 'Text_Files')


# url = 'https://drive.google.com/uc?id=1pnRT9we46ex4KO-my1DyjhIMHodS1gHd'
# output = 'WordEmbeddings.zip'
# gdown.download(url, output, quiet=False, verify=False)
# shutil.unpack_archive('WordEmbeddings.zip', 'WordEmbeddings')



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


##### word2vec model
embeddingsize = 70
win_size =  5
sentences = MySentences(corpus) # a memory-friendly iterator 
loss_logger = LossLogger(wordembedding_dir, embeddingsize , win_size) #LossLogger Class from custom utility module
model = Word2Vec(sentences,vector_size=embeddingsize, window=win_size,compute_loss=True,min_count=2, workers=1, epochs=70,callbacks=[loss_logger])   #create model and save log files 
