from infer_product_category import allowed_categories, allowed_colors, allowed_genders, allowed_product_names

STARTER_PROMPT = f"""As an AI fashion concierge, you're an interactive chat agent for users shopping on Turtleson, an online lifestyle apparel brand. Turtleson offers a variety of products, from outerwear and polos to pants and shoes. It caters to active lifestyles, with collections such as Essentials, Accessories, Summer Looks, and Women’s Polos.

You'll help users select individual items or entire outfits with style advice, based on their needs. You will also answer any questions about the store, given the information that you have.

If you don't need to select pieces or an outfit, call the display_user_text_message function.

Be succinct but descriptive in your answers. Limit the text to 125 words or less

When curating items or outfits,
1. Generate possible pieces that could exist at this store and match the user's preferences
2. Call find_store_pieces with these generated pieces
3. Select the pieces to create the best outfit or the best few items based on the return value of find_store_pieces. Do not select multiple pieces with the same name.
4. Call display_user_message_with_pieces. Ensure the selected pieces have different names
"""

def create_function_descriptions(product_ids):
  return [
    {
      'name': 'find_store_pieces',
      'description': 'Returns an array of real piece options from the retailer based on the generated pieces',
      'parameters': {
          'type': 'object',
          'required': ['pieces'],
          'properties': {
            'pieces': {
              'type': 'array',
              'items': {
                'type': 'object',
                'required': ['name', 'piece_description', 'gender', 'colors', 'piece_type'],
                'properties': {
                  'name': {
                    'type': 'string',
                    'description': 'a highly descriptive name of the clothing piece, covering key aspects such as style, material, and any distinctive features'
                  },
                  'piece_description': {
                    'type': 'string',
                    'description': 'an in-depth description of the clothing piece, detailing its style, cut, design, materials, key features, and any other relevant aspects'
                  },
                  'gender': {
                    'type': 'string',
                    'description': 'Gender of the piece. Select one of the allowed options: {allowed_genders}',
                    'enum': allowed_genders
                  },
                  'colors': {
                    'type': 'array',
                    'items': {
                      'type': 'string',
                      'description': 'Color of the piece. Select one of the allowed options: {allowed_colors}',
                      'enum': allowed_colors
                    },
                    'description': 'An array of allowed colors for the outfit.'
                  },
                  'piece_type': {
                    'type': 'string',
                    'description': 'Category of the piece. Select one of the allowed options: {allowed_categories}',
                    'enum': allowed_categories
                  }
                }
              }
          }
        }
      }
    },
    {
        'name': 'display_user_message_with_pieces',
        'description': 'Formats and displays a message with fashion pieces to the user in a chatbot interface',
        'parameters': {
            'type': 'object',
            'required': ['text', 'piece_ids'],
            'properties': {
                'text': {
                    'type': 'string',
                    'description': 'Text-only message to display to the user. Should respond to the previous user message and explain why the selected outfit or pieces works'
                },
                'piece_ids': {
                    'type': 'array',
                    'items': {
                      'type': 'integer',
                      'description': 'The Piece ID of a selected piece. Only select pieces that are directly relevant. Never select multiple pieces with the same name.',
                      'enum': product_ids
                    },
                }
            }
        }
    },
    {
        'name': 'display_user_text_message',
        'description': 'Displays a text-only message to the user in a chatbot interface. Only call this after find_store_pieces is called.',
        'parameters': {
            'type': 'object',
            'required': ['message'],
            'properties': {
              'message': {
                'type': 'string',
                'description': 'Message to display to the user. Should directly answer the user\'s last message. Strictly do not answer questions unrelated to your role as a chat agent for this store.'
              }
            }
        },
    }
  ]