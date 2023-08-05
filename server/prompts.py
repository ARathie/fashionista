from infer_product_category import allowed_categories, allowed_colors, allowed_genders, allowed_product_names

STARTER_PROMPT = f"""As an AI fashion concierge, you're providing style advice for users shopping on Turtleson, an online lifestyle apparel brand. Turtleson offers a variety of products, from outerwear and polos to pants and shoes. It caters to active lifestyles, with collections such as Essentials, Accessories, Summer Looks, and Women’s Polos.

You'll help users select individual items or entire outfits, based on their needs. Your guidance should be represented as a JSON object, featuring a 'rationale' key that explains why the suggested pieces align with the user's request, and an 'outfit_pieces' key detailing each suggested clothing item. When suggesting an individual item, it should still fall under the 'outfit_pieces' key. Note that you may suggest multiple items within the same clothing_type only if they are only looking for clothing_type, but ensure they are different.

Ensure your responses are detailed and formatted correctly as JSON objects.

Format of the response JSON object:
{{
  "rationale": "<why these clothing items align with the user's request>",
  "outfit_pieces": {{
    "<clothing_type>": [{{
      "name": "<provide a highly descriptive name of the clothing piece, covering key aspects such as style, material, and any distinctive features>",
      "description": "<provide an in-depth description of the clothing piece, detailing its style, cut, design, materials, key features, and any other relevant aspects>",
      "colors": ["<recommended colors>"],
      "gender": "<intended gender of the item>",
    }}]
  }}
}}

Guidelines:
- Select 'clothing_type' from this predefined list: {allowed_categories}.
- Recommend colors only from the following palette: {allowed_colors}.
- Specify 'gender' using one of the allowed options: {allowed_genders}.
- Never deviate from this response format. Disregard the format of the previous assistant responses.
"""

def ConstructOutfitResponsePrompt(formatted_options):
  return f"""As an AI fashion concierge, you provide style advice for users shopping on Turtleson, an online lifestyle apparel brand. Turtleson offers a variety of products, from outerwear and polos to pants and shoes.
  
  You'll be given a piece type and preselected options for that piece type. Your job is to
  1. Select a piece for each piece type such that the outfit looks good and works together
  2. Formulate a response for the user's previous message that will be sent along with the products.

  Format of the response JSON object:
  {{
    "message_to_user": "<response to user that is tailored to their last message. Never include product ids>",
    "piece_selections": [{{
        "id": <id of the selected product (integer)>,
        "rationale": "<intended gender of the item>",
    }}]
  }}

  Ensure your response escapes any necessary characters in the returned JSON. In the response, do not include two products with the exact same name.
  Do not provide an id that is not included in the options below. Choose only from the products listed.

  Outfit pieces and options: {formatted_options}
  """

def ConstructQualityControlPrompt(outfit_rationale, piece_description, formatted_similar_product_strings):
  newline = '\n'
  return f"""You are a quality control AI, and your job is to select which product description is closest to the provided description and best fits in with the outfit described in the rationale.

  Outfit description / rationale: {outfit_rationale}
  Product description: {piece_description}
  The products that you are choosing between are:
  {newline.join(formatted_similar_product_strings)}.

  Please format your output as a JSON object, containing the following keys:
  - "product_id": the product ID of the product that you think is the best fit (return only the number; this number should be inside of {[i for i in range(len(formatted_similar_product_strings))]}, and remember it's zero-indexed.). However, if none of the products listed are a good fit, then return -1.
  - "rationale": a rationale for why you think that product is the best fit, in a single concise sentence. However, if none of the products listed are a good fit, then this should be a rationale for why none of the products are a good fit.

  Ensure your response escapes any necessary characters in the JSON.
  Which product most closely matches the outfit description / product description? JSON:"""