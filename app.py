from flask import Flask, request, jsonify, render_template
import pickle
import boto3
import pandas
import numpy
from io import BytesIO

app = Flask(__name__)

health_status = True

# Configuration variables
BUCKET_NAME = 'recommendation-pipeline-output'
PICKLE_FILE_KEY = 'model.pkl'

s3 = boto3.client('s3')
response = s3.get_object(Bucket=BUCKET_NAME, Key=PICKLE_FILE_KEY)
model_str = response['Body'].read()

model_stream = BytesIO(model_str)
indices, cosine_sim_matrix, movie = pickle.load(model_stream)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/v1/recommend', methods=['POST'])
def content_recommendation_api( ):
    title = request.json.get('title')
    title = title.lower()
    index = indices[title]
    similarity_scores = list(enumerate(cosine_sim_matrix[index]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    similarity_scores = similarity_scores[0:10]
    movieindices = [i[0] for i in similarity_scores]
    print(movie['name'].iloc[movieindices].to_list()[:3])
    return jsonify(movie['name'].iloc[movieindices].to_list(),200)

@app.route('/recommend', methods=['GET'])
def content_recommendation( ):
    title = request.args.get('title')
    number_of_recommendation = request.args.get('number')

    title = title.lower()
    try:
        number_of_recommendation = int(number_of_recommendation)
        index = indices[title]
        similarity_scores = list(enumerate(cosine_sim_matrix[index]))
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        similarity_scores = similarity_scores[0:10]
        movieindices = [i[0] for i in similarity_scores]
        print(movie['name'].iloc[movieindices])
        recommended_movies = movie['name'].iloc[movieindices]

        if recommended_movies.empty:
                return render_template('recommend.html', recommendations=None)
        else:
            return render_template('recommend.html', recommendations=recommended_movies.tolist()[:number_of_recommendation])
    except:
        return render_template('recommend.html', recommendations=None)

@app.route('/health')
def health():
    if health_status:
        resp = jsonify(health="healthy")
        resp.status_code = 200
    else:
        resp = jsonify(health="unhealthy")
        resp.status_code = 500

    return resp


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
