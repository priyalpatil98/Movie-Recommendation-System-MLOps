# File to provide url/API of app using ngix/gunicorn server (Flask framework)

from flask import Flask, request, jsonify
import pickle
import boto3
from io import BytesIO

app = Flask(__name__)

health_status = True

# Configuration variables
BUCKET_NAME = 'recommendation-pipeline-output'
PICKLE_FILE_KEY = 'model.pkl'

s3 = boto3.client('s3')
response = s3.get_object(Bucket=BUCKET_NAME, Key=PICKLE_FILE_KEY)
model_str = response['Body'].read()
indices, cosine_sim_matrix, movie = pickle.load(model_str)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/health')
def health():
    if health_status:
        resp = jsonify(health="healthy")
        resp.status_code = 200
    else:
        resp = jsonify(health="unhealthy")
        resp.status_code = 500

    return resp

@app.route('/recommend', methods=['POST'])
def content_recommendation(title, similarity = cosine_sim_matrix):
    title = request.json.get('title')
    title = title.lower()
    index = indices[title]
    similarity_scores = list(enumerate(similarity[index]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    similarity_scores = similarity_scores[0:10]
    movieindices = [i[0] for i in similarity_scores]
    return jsonify(movie['name'].iloc[movieindices])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
