# File to provide url/API of app using ngix/gunicorn server (Flask framework)

from flask import Flask, request, jsonify
import model  # model.py

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict(title, num, sim_type):
    data = request.get_json()
    response = model.recommendation(data, num = num, sim_type = sim_type)  # Calling Recommendation function in model.py
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
