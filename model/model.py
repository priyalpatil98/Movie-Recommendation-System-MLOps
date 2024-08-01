# Model Training File

#!/usr/bin/env python
# coding: utf-8

# In[1]:

import boto3
import pandas as pd
import matplotlib.pyplot as plt
import sagemaker
from sagemaker import get_execution_role
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# In[2]:

# get_ipython().run_line_magic('pip', 'install seaborn')
# get_ipython().run_line_magic('pip', 'install s3fs')

# In[3]:

role = get_execution_role()
bucket = 'mlops-datasets-movie/Movies'
data_keywords = 'keywords.csv'
data_location_1 = 's3://{}/{}'.format(bucket, data_keywords)

data_credits = 'credits.csv'
data_location_2 = 's3://{}/{}'.format(bucket, data_credits)

data_metadata = 'movies_metadata.csv'
data_location_3 = 's3://{}/{}'.format(bucket, data_metadata)

movie_keywords = pd.read_csv(data_location_1)
movie_credits = pd.read_csv(data_location_2)
movie_md = pd.read_csv(data_location_3)

# In[4]:

movie_md = movie_md[movie_md['id'].str.isnumeric()] # Removing the records for which the id is not available
movie_md['id'] = movie_md['id'].astype(int)
movie_md = movie_md[movie_md['vote_count']>=30]
movie_md = movie_md[['id','original_title','overview','genres','release_date','revenue','runtime','original_language', 'vote_count', 'vote_average']]
movie_md['title'] = movie_md['original_title'].copy()

#Making tags column
df = pd.merge(movie_md, movie_keywords, on='id', how='left')
df = pd.merge(df, movie_credits, on='id', how='left')
df.reset_index(inplace=True, drop=True)

df['genres'] = df['genres'].apply(lambda x: [i['name'] for i in eval(x)])
df['genres'] = df['genres'].apply(lambda x: ' '.join([i.replace(" ","") for i in x]))

df['keywords'].fillna('[]', inplace=True)
df['keywords'] = df['keywords'].apply(lambda x: [i['name'] for i in eval(x)])
df['keywords'] = df['keywords'].apply(lambda x: ' '.join([i.replace(" ",'') for i in x]))

df['cast'].fillna('[]', inplace=True)
df['cast'] = df['cast'].apply(lambda x: [i['name'] for i in eval(x)])
df['cast'] = df['cast'].apply(lambda x: ' '.join([i.replace(" ",'') for i in x]))

df['tags'] = df['genres'] +  ' ' + df['original_title'] + ' ' + df['keywords'] + ' ' + df['cast']
df=df[["id", "title", "overview", "tags"]]
df.dropna(inplace=True)
df.drop_duplicates(inplace=True)

# In[5]:

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
tfidf = TfidfVectorizer(max_features=5000)
df['overview'] = df['overview'].astype(str)
vectorized_data = tfidf.fit_transform(df['overview'].values)
vectorized_dataframe = pd.DataFrame(vectorized_data.toarray(), index=df['overview'].index.tolist())
svd = TruncatedSVD(n_components=3000)
reduced_data = svd.fit_transform(vectorized_dataframe)
df["overview"] = df["overview"].astype(object)
reduced_data.tofile("final_data.csv")
for i in range(len(df)):
    df["overview"].iloc[i]=reduced_data[i]
df.head(5)

# In[22]:

from sklearn.metrics.pairwise import cosine_similarity

similarity_cosine = cosine_similarity(reduced_data)

def recommendation(movie_title, num, sim_type):
    id_of_movie = df[df['title']==movie_title].index[0]
    if sim_type=="cosine":
        print("Using similarity_cosine")
        distances = similarity_cosine[id_of_movie]
    else:
        print("Invalid Input")
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:num]
    
    title_list=[]
    id_list=[]
    for i in movie_list:
        title_list=title_list+[df.iloc[i[0]].title]
        id_list=id_list+[df.iloc[i[0]].id]
    return(id_list, title_list)

# In[35]:

#recommendation('2012',21, "cosine")[1]
