# File to provide url/API of app using ngix/gunicorn server (Flask framework)

from flask import Flask, request, jsonify
#import model  # model.py

app = Flask(__name__)

health_status = True

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# @app.route('/predict', methods=['POST'])
# def predict(title, num, sim_type):
#     data = request.get_json()
#     response = model.recommendation(data, num = num, sim_type = sim_type)  # Calling Recommendation function in model.py
#     return jsonify(response)
    
@app.route('/test', methods=['GET', 'POST'])
def test_connection():
    # Log the request details
    if request.method == 'POST':
        data = request.get_json()  # Assuming a JSON payload
        print(f"Received POST request with data: {data}")
    else:
        print("Received GET request")
    
    # Acknowledge the request
    return jsonify({"status": "success", "message": "Request received successfully."}), 200

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
