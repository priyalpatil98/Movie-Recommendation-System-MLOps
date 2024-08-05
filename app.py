# File to provide url/API of app using ngix/gunicorn server (Flask framework)

from flask import Flask, request, jsonify

app = Flask(__name__)

health_status = True

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
