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
        else:
            role = "assistant"
        
        messages_to_send.append({
            "role": role,
            "content": message['content']
        })
    return messages_to_send

# Searches for the closest piece of clothing to the outfit piece that is passed in.
def search_for_potential_pieces(outfit_piece, num_products_to_consider=3):
    # Search through the database for the products that match the outfit pieces
    piece_name = outfit_piece["name"]
    piece_description = outfit_piece["piece_description"]
    gender = outfit_piece["gender"]
    colors = outfit_piece["colors"]
    piece_type = outfit_piece["piece_type"]

    # Make a string that can be embedded into the database and is useful for searching
    embeddable_text = f"Product Name: {piece_name}; Description: {piece_description}; Color: {', '.join(colors)}"

    return db_functions.find_similar_products(embeddable_text, piece_type, gender, num_closest_products=num_products_to_consider, store_name='turtleson')

def call_gpt(messages):
    openai_response = openai_utils.openai_response_multiple_messages(messages)
    print("openai_response: ", openai_response)

    if openai_response.get('function_call') == None:
        print("no functions called :(")

        message = openai_response.get("content", None)
        if message == None:
            return "couldn\'t find a response", [], []
        return message, [], []


    # Extracting the arguments of the function call
    function_args = json.loads(openai_response['function_call']['arguments'])

    if openai_response['function_call']['name'] == "display_user_text_message":
        # return the message 
        return function_args['message'], [], []
        
    # Checking to see which specific function call was invoked
    if openai_response['function_call']['name'] != "find_store_pieces":
        print("find_store_pieces not called, throw error")
        return "find_store_pieces not called, throw error", [], []

    matched_pieces, product_id_to_details = find_store_pieces(function_args['pieces'])

    messages.append({
        "role": "assistant",
        "content": None,
        "function_call": {
            "name": "find_store_pieces",
            "arguments": f'{function_args}'
        }
    })

    messages.append({
        "role": "function",
        "name": "find_store_pieces",
        "content": f'{matched_pieces}'
    })

    print("messages: ", messages)

    openai_response = openai_utils.openai_response_multiple_messages(messages, list(product_id_to_details.keys()))
    print("openai_response: ", openai_response)

    if openai_response.get('function_call') == None or openai_response['function_call']['name'] != "display_user_message_with_pieces":
        print("display_user_message_with_pieces not called, throw error")
        return "display_user_message_with_pieces not called, throw error", [], []

    # Extracting the arguments of the function call
    function_args = json.loads(openai_response['function_call']['arguments'])

    return function_args['text'], function_args['piece_ids'], [product_id_to_details[piece_id] for piece_id in function_args['piece_ids']]

def find_store_pieces(input_pieces):
    matched_pieces = []
    product_id_to_details = {}

    for piece in input_pieces:
        potential_matches = search_for_potential_pieces(piece)
        
        for match in potential_matches:
            product_id, description, colors, name = match[0], match[2], match[3], match[5]
            matched_pieces.append([f"Piece ID: {product_id}, Name: {name}, Description: {description}, Colors: {colors}"])
            product_id_to_details[product_id] = {
                "name": match[5],
                "description": match[2],
                "tags": match[4],
                "image_urls": match[8],
                "price": match[6],
                "url": match[7],
                "product_id": match[0],
            }

    return matched_pieces, product_id_to_details
