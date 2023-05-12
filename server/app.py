# A minimal flask app for "Hello World"

from flask import Flask, jsonify, request
import db_functions
import time, json
import openai_utils
from infer_product_category import allowed_categories, allowed_colors, allowed_genders


app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"


# POST request for inserting user into database
@app.route("/insert_user_into_db", methods=['POST'])
def insert_user_into_db():
    print("Got a POST request")
    request_data = request.get_json()
    email = request_data.get('email')
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
        # "content": """You are a fashion concierge, who is helping advise someone on purchasing an outfit from an online shopping website. The user will give you a description of the type of outfit that they would like to be wearing, and you will return a JSON object containing an "outfit_pieces" key, which is an object containing multiple outfit pieces (like "top: <shirt_description>, bottom: <pants_description>", etc), along with a “rationale” key stored inside the JSON object. This rationale will address why the various pieces fit together with each other and how they fit in with what the user asked for, and will be returned directly to the user in a chat window so it should be conversational in nature. Please output only this JSON object, and when you are producing the JSON object, please produce the “rationale” key first. In later parts of the conversation, you will update the outfit based on user feedback. Additionally, be relatively descriptive with your returned product descriptions. The conversation will now begin, and remember, each time you respond, you will respond with correctly formatted JSON."""
        "content": f"""You are a fashion concierge, who is helping advise someone on purchasing an outfit from an online shopping website. The user will give you a description of the type of outfit that they would like to be wearing, and you will return a JSON object containing an "outfit_pieces" key, which is an object containing multiple outfit pieces (like "top: <shirt_description>, bottom: <pants_description>", etc), along with a “rationale” key stored inside the JSON object. This rationale will address why the various pieces fit together with each other and how they fit in with what the user asked for, and will be returned directly to the user in a chat window so it should be conversational in nature. In later parts of the conversation, you will update the outfit based on user feedback. Additionally, be relatively descriptive with your returned product descriptions. The conversation will now begin, and remember, each time you respond, you will respond with correctly formatted JSON. Also, realize that in some cases, you won't need to output the full JSON object, and can instead just output the "rationale" key (for example, when the user is asking more general questions about their style)

Please return a JSON object with the following format, in the following order (remember, ONLY provide the keys that are specified below, nothing else):
{{
  "rationale": <rationale for the output>,
  "outfit_pieces": {{
    <clothing_type>: {{
      "description": <descriptive description of the piece of clothing>,
      "colors": [<colors of the piece of clothing>],
      "gender": <gender that it's for>
    }}
  }}
}}

Rules:
- the outfit_pieces can only contain the following categories as keys: {allowed_categories}.
- when choosing colors, you can only recommend colors from the following: {allowed_colors}. Please recommend multiple colors that would work.
- when specifying the gender, you can only use the following: {allowed_genders}"""
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


# POST request for messaging
@app.route("/post", methods=['POST'])
def post():
    print("Got a POST request")
    request_data = request.get_json()
    message = request_data.get('message')
    email = request_data.get('email')
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
        print("Got rationale: ", rationale)
        # Get the outfit pieces
        outfit_pieces = json_response["outfit_pieces"]
        print("Got outfit pieces: ", outfit_pieces)

        pieces_to_return = []
        product_ids = []
        for piece_type in outfit_pieces.keys():
            # Search through the database for the products that match the outfit pieces
            print("Searching for products that match the outfit pieces")
            outfit_piece = outfit_pieces[piece_type]
            piece_description = outfit_piece["description"]
            gender = outfit_piece["gender"]
            colors = outfit_piece["colors"]

            num_products_to_return = 3

            # Make a string that can be embedded into the database and is useful for searching
            embeddable_text = f"Type: {piece_type}; Description: {piece_description}; Colors: {', '.join(colors)}"

            # Search for the products that match the outfit piece
            similar_products = db_functions.find_similar_products(embeddable_text, piece_type, gender, num_closest_products=num_products_to_return, store_name='asos')

            # If there are no products that match the outfit piece, then just continue.
            if len(similar_products) == 0:
                continue

            # Get the first product from the list of similar products
            # print("Got similar products: ", similar_products)
            formatted_similar_product_strings = [f"[{index}] Name: {product[5]}, Description: {product[2]}" for index, product in enumerate(similar_products)]

            # Use OpenAI to take in the descriptions and names of the products that were returned, along with the high-level rationale for the outfit + the product description that was used to search for the products, and return which product should be chosen of the ones that were returned
            newline = '\n'
            prompt = f"""You are a quality control AI, and your job is to select which product description is closest to the provided description and best fits in with the outfit described in the rationale.

Outfit description / rationale: {rationale}
Product description: {piece_description}
The products that you are choosing between are:
{newline.join(formatted_similar_product_strings)}.

Please format your output as a JSON object, containing the following keys:
- "product_id": the product ID of the product that you think is the best fit (return only the number; this number should be inside of {[i for i in range(len(formatted_similar_product_strings))]}, and remember it's zero-indexed.)
- "rationale": a rationale for why you think that product is the best fit, in a single concise sentence

Which product most closely matches the outfit description / product description? JSON:"""
            print(f"About to get response from OpenAI. Request: {prompt}")
            validation_response = openai_utils.openai_response(prompt)
            print("Got response from OpenAI: ", validation_response)
            # Get the index of the product that was chosen
            product_index = json.loads(validation_response)['product_id']
            # product_index = int(validation_response)
            print("Got product index: ", product_index)
            print("Type of product index: ", type(product_index))
            if type(product_index) == list:
                product_index = product_index[0]
            # Get the product that was chosen
            product = similar_products[product_index]

            # Get the product name, description, tags, and other info
            # TODO: Make this not based on index; should be based on name
            name = product[5]
            description = product[2]
            tags = product[4]
            image_urls = product[8]
            price = product[6]
            url = product[7]
            product_id = product[0]

            # Add the product info to the list of pieces to return
            pieces_to_return.append({
                "name": name,
                "description": description,
                "tags": tags,
                "image_urls": image_urls,
                "price": price,
                "url": url
            })

            # Add the product id to the list of product ids
            # TODO: Make these be associated to the bot's output, instead of just a list (I guess it kinda already is, though, good to make it more explicit, though)
            product_ids.append(product_id)
        
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
    except Exception as e:
        print(e)
        # return jsonify(error="Error parsing response"), 500

    return jsonify(text=response)


# POST request for inserting product info into the database
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
