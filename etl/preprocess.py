# Preprocessing python file for etl
import os
import tempfile
import numpy as np
import pandas as pd
import datetime as dt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

if __name__ == "__main__":
    base_dir = "/opt/ml/processing"
    
    #Read Data
    movie_keywords = pd.read_csv(
        f"{base_dir}/input/movie_keywords.csv"
    )
    
    movie_credits = pd.read_csv(
        f"{base_dir}/input/movie_credits.csv"
    )
    
    movie_md = pd.read_csv(
        f"{base_dir}/input/movie_md.csv"
    )
    

    # Data Pre-Processing
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
    
    # Rearranging Features in Dataset
    df=df[["id", "title", "overview", "tags"]]
    
    # Drop Empty Values & Removing Duplicates
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    

    # 
    tfidf = TfidfVectorizer(max_features=5000)
    df['overview'] = df['overview'].astype(str)
    vectorized_data = tfidf.fit_transform(df['overview'].values)
    vectorized_dataframe = pd.DataFrame(vectorized_data.toarray(), index=df['overview'].index.tolist())
    svd = TruncatedSVD(n_components=3000)
    reduced_data = svd.fit_transform(vectorized_dataframe)
    df["overview"] = df["overview"].astype(object)
    for i in range(len(df)):
        df["overview"].iloc[i]=reduced_data[i]
    df.head(5)
    
    # Save the Dataframes as csv files
    # train.to_csv(f"{base_dir}/train/train.csv", header=False, index=False)
    # validation.to_csv(f"{base_dir}/validation/validation.csv", header=False, index=False)
    # test.to_csv(f"{base_dir}/test/test.csv", header=False, index=False)