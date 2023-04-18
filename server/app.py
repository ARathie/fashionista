# A minimal flask app for "Hello World"

from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

# POST request
@app.route("/post", methods=['POST'])
def post():
    # Return a JSON response with the text field set to "hello world!"
    return jsonify(text="hello world!")


if __name__ == "__main__":
    app.run()
