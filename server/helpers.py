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
    messages_to_send = append_formatted_messages(messages_to_send, messages)
    return messages_to_send

def format_messages_with_response_prompt(messages, response_prompt_input):
    """Formats messages into a format that OpenAI can understand."""
    messages_to_send = []
    messages_to_send.append({
        "role": "system",
        "content": prompts.ConstructOutfitResponsePrompt(response_prompt_input)
    })
    messages_to_send = append_formatted_messages(messages_to_send, messages)
    return messages_to_send

def append_formatted_messages(message_arr, messages):
    for message in messages:
        if message["sent_from_user"]:
            role = "user"
            message_content = f"User Query: {message['content']}\n\nJSON Output:"
        else:
            role = "assistant"
            message_content = message['content']
        
        message_arr.append({
            "role": role,
            "content": message_content
        })
    return message_arr


# Searches for the closest piece of clothing to the outfit piece that is passed in.
def search_for_potential_pieces(outfit_piece, piece_type, num_products_to_consider=3):
    # Search through the database for the products that match the outfit pieces
    piece_name = outfit_piece["name"]
    piece_description = outfit_piece["description"]
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
def finalize_pieces_and_get_text_response(potential_product_tuples, messages):
    # Use OpenAI to take in the descriptions and names of the products that were returned, along with the high-level rationale for the outfit + the product description that was used to search for the products, and return which product should be chosen of the ones that were returned
    formatted_options = []
    product_id_to_product = {}
    for potential_product_tuple in potential_product_tuples:
        if potential_product_tuple[1] == None:
            continue
        formatted_similar_product_string = '\n'.join([f"[{product[0]}] - Name: {product[5]}, Description: {product[2]}, Colors: {product[3]}" for index, product in enumerate(potential_product_tuple[1])])
        formatted_options.append(potential_product_tuple[0] +':\n' + formatted_similar_product_string +'\n\n')
        for product in potential_product_tuple[1]:
            product_id_to_product[product[0]] = product
   
    print("product_id_to_product: ", product_id_to_product)
    response = openai_utils.openai_response_multiple_messages(format_messages_with_response_prompt(messages, formatted_options))
    
    response_json = json.loads(response)
    piece_selections = response_json['piece_selections']
    print("product_id_to_product: ", product_id_to_product)
    print("response_json: ", response_json)

    selected_product_ids = [selection['id'] for selection in piece_selections]
    selected_products = [product_id_to_product[id] for id in selected_product_ids]

    formatted_selected_products = []
    for product in selected_products:
        formatted_product = {
            "name": product[5],
            "description": product[2],
            "tags": product[4],
            "image_urls": product[8],
            "price": product[6],
            "url": product[7],
            "product_id": product[0],
        }
        formatted_selected_products.append(formatted_product)

    return response, response_json, formatted_selected_products