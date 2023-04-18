# A minimal flask app for "Hello World"

from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

# POST request
@app.route("/post", methods=['POST'])
def post():
    request_data = request.get_json()
    message = request_data.get('message')
    if message is None:
        return jsonify(error="message field is required"), 400
    return jsonify(text=message)


if __name__ == "__main__":
    app.run()
