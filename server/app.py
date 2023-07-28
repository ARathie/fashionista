# A minimal flask app for "Hello World"

from flask import Flask, jsonify, request
import db_functions
import time, json
import openai_utils
from infer_product_category import allowed_categories, allowed_colors, allowed_genders

import constants
import twilio_helpers

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
    email = "abhinav.rathie@gmail.com"
    if email is None:
        return jsonify(error="email field is required"), 400

    # Insert the user into the database
    user_info = {
        "email": email
    }
    db_functions.insert_user_into_db(user_info)

    return jsonify(success=True), 200


def format_messages_with_starter_prompt(messages):
    """Formats messages into a format that OpenAI can understand."""
    messages_to_send = []
    messages_to_send.append({
        "role": "user",
        # "content": f"""You are a fashion concierge, who is helping advise someone on purchasing an outfit from an online shopping website. The user will give you a description of the type of outfit that they would like to be wearing, and you will return a JSON object containing an "outfit_pieces" key, which is an object containing multiple outfit pieces (like "top: <shirt_description>, bottom: <pants_description>", etc), along with a “rationale” key stored inside the JSON object. This rationale will address why the various pieces fit together with each other and how they fit in with what the user asked for, and will be returned directly to the user in a chat window so it should be conversational in nature. Please output only this JSON object, and when you are producing the JSON object, please produce the “rationale” key first. In later parts of the conversation, you will update the outfit based on user feedback. Additionally, be relatively descriptive with your returned product descriptions. The conversation will now begin, and remember, each time you respond, you will respond with correctly formatted JSON."""
        "content": f"""As an AI fashion concierge, you're providing style advice for users shopping on Turtleson, an online lifestyle apparel brand. Turtleson offers a variety of products, from outerwear and polos to pants and shoes. It caters to active lifestyles, with collections such as Essentials, Accessories, Summer Looks, and Women’s Polos.

You'll help users select individual items or entire outfits, based on their needs. Your guidance should be represented as a JSON object, featuring a 'rationale' key that explains why the suggested pieces align with the user's request, and an 'outfit_pieces' key detailing each suggested clothing item. When suggesting an individual item, it should still fall under the 'outfit_pieces' key. Note that you may suggest multiple items within the same clothing_type only if they are only looking for clothing_type, but ensure they are different.

Ensure your responses are detailed and formatted correctly as JSON objects.

Format of the response JSON object:
{{
  'rationale': '<why these clothing items align with the user's request>',
  'outfit_pieces': {{
    '<clothing_type>': [{{
      'description': '<descriptive details of the clothing piece>',
      'colors': ['<recommended colors>'],
      'gender': '<intended gender of the item>'
    }}]
  }}
}}

Guidelines:
- Select 'clothing_type' from this predefined list: {allowed_categories}.
- Recommend colors only from the following palette: {allowed_colors}.
- Specify 'gender' using one of the allowed options: {allowed_genders}.
"""

        
        
#         """You are a fashion concierge, who is helping advise someone on purchasing an outfit from an online shopping website. The user will give you a description of the type of outfit that they would like to be wearing, and you will return a JSON object containing an "outfit_pieces" key, which is an object containing multiple outfit pieces (like "top: <shirt_description>, bottom: <pants_description>", etc), along with a “rationale” key stored inside the JSON object. This rationale will address why the various pieces fit together with each other and how they fit in with what the user asked for, and will be returned directly to the user in a chat window so it should be conversational in nature. In later parts of the conversation, you will update the outfit based on user feedback. Additionally, be relatively descriptive with your returned product descriptions. The conversation will now begin, and remember, each time you respond, you will respond with correctly formatted JSON. Also, realize that in some cases, you won't need to output the full JSON object, and can instead just output the "rationale" key (for example, when the user is asking more general questions about their style)

# Please return a JSON object with the following format, in the following order (remember, ONLY provide the keys that are specified below, nothing else):
# {{
#   "rationale": <rationale for the output>,
#   "outfit_pieces": {{
#     <clothing_type>: {{
#       "description": <descriptive description of the piece of clothing>,
#       "colors": [<colors of the piece of clothing>],
#       "gender": <gender that it's for>
#     }}
#   }}
# }}

# Rules:
# - the outfit_pieces can only contain the following categories as keys: {allowed_categories}.
# - when choosing colors, you can only recommend colors from the following: {allowed_colors}. Please recommend multiple colors that would work.
# - when specifying the gender, you can only use the following: {allowed_genders}"""
    })
    for message in messages:
        if message["sent_from_user"]:
            role = "user"
            message_content = f"User Query: {message['content']}\n\nJSON Output:"
            print(f"User Query: {message['content']}")
        else:
            role = "assistant"
            message_content = message['content']
            print(f"Assistant Response: {message_content}")
        
        messages_to_send.append({
            "role": role,
            "content": message_content
        })
    return messages_to_send


def search_for_outfit_piece(outfit_piece, piece_type, outfit_rationale, num_products_to_consider=3):
    """Searches for the closest piece of clothing to the outfit piece that is passed in.
    Also uses completion API to further refine which product is chosen."""
    # Search through the database for the products that match the outfit pieces
    piece_description = outfit_piece["description"]
    gender = outfit_piece["gender"]
    colors = outfit_piece["colors"]

    # Make a string that can be embedded into the database and is useful for searching
    embeddable_text = f"Type: {piece_type}; Description: {piece_description}; Colors: {', '.join(colors)}"

    # Search for the products that match the outfit piece
    similar_products = db_functions.find_similar_products(embeddable_text, piece_type, gender, num_closest_products=num_products_to_consider, store_name='turtleson')

    # If there are no products that match the outfit piece, then just continue.
    if len(similar_products) == 0:
        return None


    # Use OpenAI to take in the descriptions and names of the products that were returned, along with the high-level rationale for the outfit + the product description that was used to search for the products, and return which product should be chosen of the ones that were returned
    formatted_similar_product_strings = [f"[{index}] Name: {product[5]}, Description: {product[2]}" for index, product in enumerate(similar_products)]
    newline = '\n'
    prompt = f"""You are a quality control AI, and your job is to select which product description is closest to the provided description and best fits in with the outfit described in the rationale.

Outfit description / rationale: {outfit_rationale}
Product description: {piece_description}
The products that you are choosing between are:
{newline.join(formatted_similar_product_strings)}.

Please format your output as a JSON object, containing the following keys:
- "product_id": the product ID of the product that you think is the best fit (return only the number; this number should be inside of {[i for i in range(len(formatted_similar_product_strings))]}, and remember it's zero-indexed.). However, if none of the products listed are a good fit, then return -1.
- "rationale": a rationale for why you think that product is the best fit, in a single concise sentence. However, if none of the products listed are a good fit, then this should be a rationale for why none of the products are a good fit.

Which product most closely matches the outfit description / product description? JSON:"""
    print(f"About to get response from OpenAI. Request: {prompt}")
    validation_response = openai_utils.openai_response(prompt)
    print("Got response from OpenAI: ", validation_response)
    # Get the index of the product that was chosen
    validation_response_json = json.loads(validation_response)
    product_index = validation_response_json['product_id']
    product_rationale = validation_response_json['rationale']

    # product_index = int(validation_response)
    print("Got product index: ", product_index)
    print("Type of product index: ", type(product_index))
    if type(product_index) == list:
        product_index = product_index[0]
    # Get the product that was chosen
    product = similar_products[product_index]

    # If the product index is -1, then that means that none of the products were a good fit - mark this in the name below, for debugging
    if product_index == -1:
        model_confident_in_returned_item = False
    else:
        model_confident_in_returned_item = True

    # Get the product name, description, tags, and other info
    # TODO: Make this not based on index; should be based on name
    name = product[5]
    description = product[2]
    tags = product[4]
    image_urls = product[8]
    price = product[6]
    url = product[7]
    product_id = product[0]

    # Return the product info
    return {
        # "name": f"{name} (Original search query: {piece_description}, Rationale when searching: {product_rationale}, Model confident in returned item: {model_confident_in_returned_item})",
        "name": f"{name}",
        "description": description,
        "tags": tags,
        "image_urls": image_urls,
        "price": price,
        "url": url,
        "product_id": product_id,
        "model_confident_in_returned_item": model_confident_in_returned_item
    }

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
    email = 'abhinav.rathie@gmail.com'
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
    messages = format_messages_with_starter_prompt(user_messages)
    print("Formatted messages: ", messages)
    response = openai_utils.openai_response_multiple_messages(messages)

    try:
        # Parse the response as a json string
        print("About to get JSON response")
        json_response = json.loads(response, strict=False)
        print("Got JSON Response: ", json_response)
        # Get the rationale
        rationale = json_response["rationale"]
        print("Got rationale2: ", rationale)
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
                piece_to_return = search_for_outfit_piece(outfit_piece, piece_type, rationale, num_products_to_consider=3)
                if piece_to_return is None:
                    continue
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

    # Return a json object with the text being the rationale, and the outfit pieces as a json dump
    print("Returning JSON response: ", {
        "text": rationale,
        "outfit_pieces": pieces_to_return
    })
    return jsonify({
        "text": rationale,
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
