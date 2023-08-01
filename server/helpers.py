import prompts
import db_functions
import openai_utils
import json

def format_messages_with_starter_prompt(messages):
    """Formats messages into a format that OpenAI can understand."""
    messages_to_send = []
    messages_to_send.append({
        "role": "system",
        "content": prompts.STARTER_PROMPT
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

# Searches for the closest piece of clothing to the outfit piece that is passed in.
def search_for_potential_pieces(outfit_piece, piece_type, num_products_to_consider=3):
    # Search through the database for the products that match the outfit pieces
    piece_name = outfit_piece["name"]
    piece_description = outfit_piece["description"]
    print(piece_description)
    gender = outfit_piece["gender"]
    colors = outfit_piece["colors"]

    # Make a string that can be embedded into the database and is useful for searching
    embeddable_text = f"Product Name: {piece_type}; Description: {piece_description}; Color: {', '.join(colors)}"

    # Search for the products that match the outfit piece
    similar_products = db_functions.find_similar_products(embeddable_text, piece_type, gender, num_closest_products=num_products_to_consider, store_name='turtleson')

    # If there are no products that match the outfit piece, then just continue.
    if len(similar_products) == 0:
        return None

    return similar_products

# Uses completion API to further refine which product is chosen."""
def select_piece(potential_products, outfit_piece, outfit_rationale):
    # Use OpenAI to take in the descriptions and names of the products that were returned, along with the high-level rationale for the outfit + the product description that was used to search for the products, and return which product should be chosen of the ones that were returned
    formatted_similar_product_strings = [f"[{index}] Name: {product[5]}, Description: {product[2]}" for index, product in enumerate(potential_products)]
    validation_response = openai_utils.openai_response(prompts.ConstructQualityControlPrompt(outfit_rationale, outfit_piece["description"], formatted_similar_product_strings))
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
    product = potential_products[product_index]

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