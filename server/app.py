# A minimal flask app for "Hello World"

from flask import Flask, jsonify, request
import db_functions
import time, json
import openai_utils

import constants
import twilio_helpers
import helpers

app = Flask(__name__)

# basic Flask route for testing that returns "Hello World!" when accessed
@app.route("/")
def hello():
    return "Hello World!"


# POST request for inserting user into database.
# Extracts the email from the request data and calls the insert_user_into_db function from the db_functions module.
@app.route("/insert_user_into_db", methods=['POST'])
def insert_user_into_db():
    print("Got a POST request")
    request_data = request.get_json()
    email = "abhinav.rathie4@gmail.com"
    if email is None:
        return jsonify(error="email field is required"), 400

    # Insert the user into the database
    user_info = {
        "email": email
    }
    db_functions.insert_user_into_db(user_info)

    return jsonify(success=True), 200

# Webhook for responding to Twilio, doing the same thing as the POST request. This should use the logic that's implemented with Twilio, but should also be able to be used with other messaging services
@app.route("/twilio_webhook", methods=['POST'])
def twilio_webhook():
    return twilio_helpers.handle_twilio_webhook_request

# flask route for handling POST request for messaging
@app.route("/post", methods=['POST'])
def post():
    try: 
        print("Got a POST request")
        request_data = request.get_json()
        message = request_data.get('message')
        email = 'abhinav.rathie4@gmail.com'
        if message is None:
            return jsonify(error="message field is required"), 400

        # Insert the user's message into the database
        user_message_info = {
            "email": email,
            "content": message,
            "sent_from_user": True,
            "product_ids": []
        }
        db_functions.insert_message_into_db(user_message_info)

        # Use the email to get the user's previous messages, and use that to generate a response
        user_messages = db_functions.get_all_messages_for_user(email)
        
        # Format the messages into a format that OpenAI can understand
        messages = helpers.format_messages_with_starter_prompt(user_messages)
        print("Formatted messages: ", messages)

        text, product_ids, outfit_pieces = helpers.call_gpt(messages)
        bot_message_info = {
            "email": email,
            "content": text,
            "sent_from_user": False,
            "product_ids": product_ids
        }
        db_functions.insert_message_into_db(bot_message_info)

        return jsonify({
            "text": text,
            "outfit_pieces": outfit_pieces
        })
    except Exception as e:
        print("got exception: ", e)
        return jsonify({
            "text": "We encountered an error. Please try again.",
            "outfit_pieces": []
        })
        
# Flask route for handling POST requests for inserting product info into the database
@app.route("/insert_product_info", methods=['POST'])
def insert_product_info():
    """Insert product info into the database."""
    request_data = request.get_json()
    price = request_data.get('price')
    name = request_data.get('name')
    description = request_data.get('description')
    image_urls = request_data.get('image_urls')
    tags = request_data.get('tags')
    url = request_data.get('url')
    raw_color = request_data.get('raw_color')
    store_name = request_data.get('store_name')
    if price is None or name is None or description is None or image_urls is None or tags is None or url is None or raw_color is None or store_name is None:
        return jsonify(error="price, name, description, image_urls, tags, url, raw_color, store_name fields are required"), 400
    
    # Check if category is in the request data - if it isn't there, set it to None
    if 'category' in request_data:
        category = request_data.get('category')
    else:
        category = None
    
    # Check if the gender is in the request data - if it isn't there, set it to None
    if 'gender' in request_data:
        gender = request_data.get('gender')
    else:
        gender = None
        
    product_info = {
        "price": price,
        "name": name,
        "description": description,
        "image_urls": image_urls,
        "tags": tags,
        "url": url,
        "raw_color": raw_color,
        "store_name": store_name,
        "category": category,
        "gender": gender
    }
    db_functions.insert_product_info_into_db(product_info)
    return jsonify(text="Product info successfully inserted into database.")


if __name__ == "__main__":
    app.run(port=5001)
