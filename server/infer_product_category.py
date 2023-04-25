import db_functions
from openai_utils import openai_response
import json

allowed_genders = ["men", "women", "unisex"]
allowed_categories = ['top', 'bottom', 'outerwear', 'dress', 'swimwear', 'underwear', 'sleepwear', 'accessory', 'footwear']
allowed_colors = ['red', 'green', 'blue', 'black', 'brown', 'grey', 'yellow', 'purple', 'white', 'pink', 'orange', 'olive', 'silver', "beige", "multi-color", "navy"]


def infer_product_category_colors_and_gender(product_info):
    """Infer the product category using the given product's description and name."""
    # Get the product info from the database
    product_name = product_info["name"]
    product_description = product_info["description"]
    product_tags = product_info["tags"]
    product_id = product_info["id"]

    # Prompt for OpenAI to infer the product category, colors, and gender, using the product name, description, and tags, in JSON format, using only the allowed categories, genders, and colors
    prompt = ""
    prompt = f"""Given the product name, description, and tags, please infer the product category, colors, and gender, in JSON format.
Name: '{product_name}'
Description: '{product_description}'
Tags: '{product_tags}'

Please perform your inference using ONLY the following allowed attributes - any other attributes will throw an error, it's important that you only use the allowed attributes:
Allowed product categories: ({', '.join(allowed_categories)})
Allowed genders: ({', '.join(allowed_genders)})
Allowed colors: ({', '.join(allowed_colors)})

Your returned JSON should have the following keys, and corrsponding values:
- gender: string
- category: string
- colors: list[string] (one string for each color, do NOT use any colors other than the allowed colors - you will likely need to infer the color from the relatively esoteric color names provided.)

JSON:"""

    json_result = openai_response(prompt)
    # print(f"Input: {prompt}")
    print(f"OpenAI response: {json_result}")

    try:
        product_info_inferred = json.loads(json_result)
    except json.JSONDecodeError:
        raise ValueError("OpenAI response could not be parsed as JSON")


    # Extract the required fields from the OpenAI response
    inferred_category = product_info_inferred["category"]
    inferred_gender = product_info_inferred["gender"]
    inferred_colors = product_info_inferred["colors"]

    # Check if the inferred category is allowed
    if inferred_category not in allowed_categories:
        raise ValueError(f"Category {inferred_category} is not allowed")
    
    # Check if the inferred gender is allowed
    if inferred_gender not in allowed_genders:
        raise ValueError(f"Gender {inferred_gender} is not allowed")
    
    # Check if the inferred colors are allowed
    for color in inferred_colors:
        if color not in allowed_colors:
            raise ValueError(f"Color {color} is not allowed")
    
    # Return them as a dictionary
    return {
        "category": inferred_category,
        "gender": inferred_gender,
        "colors": inferred_colors
    }

if __name__ == "__main__":
    # Take in user input for the types of products that are the most important to infer
    product_type_to_infer = input("What type of product do you want to infer for? ")
    limit = int(input("How many products do you want to infer for? "))

    # Get the uncategorized products
    uncategorized_products = db_functions.get_uncategorized_products_from_db(limit=limit, bias_towards_prompt = product_type_to_infer)
    # print("Uncategorized products: ", uncategorized_products)

    # Infer the category for each product
    for product in uncategorized_products:
        # Try to infer attributes
        try:
            print(f"Production Description: {product['description']}")
            inferred_attributes = infer_product_category_colors_and_gender(product)
        except Exception as e:
            print(f"Error inferring attributes for product {product}: {e}")
            continue

        # Update the product in the database
        category = inferred_attributes["category"]
        colors = inferred_attributes["colors"]
        gender = inferred_attributes["gender"]
        product_id = product["id"]
        db_functions.update_product_category_colors_and_gender(product_id, category, colors, gender)

