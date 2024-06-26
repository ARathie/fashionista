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
    response = openai_utils.openai_response_multiple_messages(messages)

    try:
        # Parse the response as a json string
        print("About to get JSON response")
        json_response = json.loads(response, strict=False)
        print("Got JSON Response: ", json_response)
        # Get the rationale
        outfit_rationale = json_response["rationale"]
        print("Got rationale2: ", outfit_rationale)
        # Get the outfit pieces
        outfit_pieces = json_response["outfit_pieces"]
        print("Got outfit pieces: ", outfit_pieces)
    except Exception as e:
        print("Got exception: ", e)
        outfit_pieces = {}

    pieces_to_return = []
    product_ids = []

    for piece_type in outfit_pieces.keys():
        # Search through the database for the products that match the outfit pieces
        outfit_piece_options = outfit_pieces[piece_type]
        
        for outfit_piece in outfit_piece_options:
            try:
                print("outfit_piece: ", outfit_piece)
                potential_products = helpers.search_for_potential_pieces(outfit_piece, piece_type, num_products_to_consider=3)
                if potential_products is None:
                    continue
                piece_to_return = helpers.select_piece(potential_products, outfit_piece, outfit_rationale)
                pieces_to_return.append(piece_to_return)
                product_ids.append(piece_to_return["product_id"])
            except Exception as e:
                print(f"Exception when searching for outfit piece: {e}")
    
    # Insert the bot's response into the database
    bot_message_info = {
        "email": email,
        "content": response,
        "sent_from_user": False,
        "product_ids": product_ids
    }
    db_functions.insert_message_into_db(bot_message_info)

    # Return a json object with the text being the outfit_rationale, and the outfit pieces as a json dump
    print("Returning JSON response: ", {
        "text": outfit_rationale,
        "outfit_pieces": pieces_to_return
    })
    return jsonify({
        "text": outfit_rationale,
        "outfit_pieces": pieces_to_return
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
