# A minimal flask app for "Hello World"

from flask import Flask, jsonify, request
import db_functions
import time, json
import openai_utils


app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

# POST request for messaging
@app.route("/post", methods=['POST'])
def post():
    print("Got a POST request")
    request_data = request.get_json()
    message = request_data.get('message')
    email = request_data.get('email')
    if message is None:
        return jsonify(error="message field is required"), 400
    
    # TODO: Use the email to get the user's previous messages, and use that to generate a response

    # Generate a response using OpenAI
    prompt = f"""You are a fashion concierge, who is helping someone on Zara.com buy products from their website. The user will give you a description of the type of outfit that they would like to be wearing, and you will return a JSON object containing an "outfit_pieces" key, which is an object containing multiple outfit pieces (like "top: <shirt_description>, bottom: <pants_description>", etc), along with a “rationale” key stored inside the JSON object. This rationale will address why the various pieces fit together with each other and how they fit in with what the user asked for, and will be returned directly to the user in a chat window so it should be conversational in nature. Please output only this JSON object, and when you are producing the JSON object, please produce the “rationale” key first. In later parts of the conversation, you will update the outfit based on user feedback. Additionally, be relatively descriptive with your returned product descriptions.\n\nUser Query: {message} \n\nJSON Output:"""
    response = openai_utils.openai_response(prompt)

    try:
        # Parse the response as a json string
        print("About to get JSON response")
        json_response = json.loads(response)
        print("Got JSON Response: ", json_response)
        # Get the rationale
        rationale = json_response["rationale"]
        print("Got rationale: ", rationale)
        # Get the outfit pieces
        outfit_pieces = json_response["outfit_pieces"]
        print("Got outfit pieces: ", outfit_pieces)

        pieces_to_return = []
        for piece_type in outfit_pieces.keys():
            # Search through the database for the products that match the outfit pieces
            print("Searching for products that match the outfit pieces")
            piece_description = outfit_pieces[piece_type]
            similar_products = db_functions.find_similar_products(f"Type: {piece_type}; Description: {piece_description}", num_closest_products=1)

            # Get the first product from the list of similar products
            print("Got similar products: ", similar_products)
            product = similar_products[0]

            # Get the product name, description, tags, and other info
            # TODO: Make this not based on index; should be based on name
            name = product[5]
            description = product[2]
            tags = product[4]
            image_urls = product[8]
            price = product[6]
            url = product[7]

            # Add the product info to the list of pieces to return
            pieces_to_return.append({
                "name": name,
                "description": description,
                "tags": tags,
                "image_urls": image_urls,
                "price": price,
                "url": url
            })
            break

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


@app.route("/search_products", methods=['POST'])
def search_products():
    """Use embedding similarity search, via cosine distance, to find the most similar products"""
    # Get the product info from the request
    request_data = request.get_json()
    name = request_data.get('name')
    description = request_data.get('description')
    tags = request_data.get('tags')

    # Get the OpenAI embedding of the description + name + str(tags)
    full_product_info = f"Product Name: {name}; Description: {description}; Tags: {str(tags)}"
    similar_products = db_functions.find_similar_products(full_product_info, num_closest_products=1)

    # Return the most similar products
    # TODO: This should return a dictionary with all the product info, made nicely so the caller can access the name / url / image_urls
    return jsonify(similar_products=similar_products)


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
    if price is None or name is None or description is None or image_urls is None or tags is None or url is None:
        return jsonify(error="price, name, description, image_urls, tags, url fields are required"), 400
    product_info = {
        "price": price,
        "name": name,
        "description": description,
        "image_urls": image_urls,
        "tags": tags,
        "url": url
    }
    db_functions.insert_product_info_into_db(product_info)
    return jsonify(text="Product info successfully inserted into database.")


if __name__ == "__main__":
    app.run()
