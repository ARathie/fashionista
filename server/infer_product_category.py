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

def infer_color_openai(description):
    """Infer the color from the given string."""
    prompt = f"""The following string is a verbose way of describing a color. Your job is to infer the color of the product, using only the allowed colors. Please return a JSON object with the following format:
{{
    "color": string
}}

The allowed colors are as follows: {', '.join(allowed_colors)}

The string to infer the color from is as follows: {description}

JSON:"""
    json_result = openai_response(prompt)
    # Load the JSON
    try:
        result = json.loads(json_result)
    except json.JSONDecodeError:
        raise ValueError("OpenAI response could not be parsed as JSON")
    # Extract the color
    color = result["color"]
    # Check if the color is allowed
    if color not in allowed_colors:
        raise ValueError(f"Color {color} is not allowed")
    # Return the color
    return color


def infer_product_category_from_nike_quick(product_info, word_to_category_map = {}):
    """Infer the product category from the product string, or from a mapping of words to categories.
    
    This mapping should be a dictionary, where the keys are words, and the values are categories, and the only 
    """


def infer_product_color_nike_quick(product_info, name_to_color_map={}):
    """Infer the product color using the given product's description."""
    # Get the product info from the database
    product_description = product_info["description"]

    # The colors are listed in the first sentence of the description - extract this, and split by '/' to get the colors
    description_sentences = product_description.split(".")
    first_sentence = description_sentences[0]
    raw_colors = first_sentence.split("/")
    print(f"Raw Colors: {raw_colors}")
    colors = []
    for color in raw_colors:
        color = color.strip().lower()
        if color in allowed_colors:
            colors.append(color)
        elif color in name_to_color_map:
            colors.append(name_to_color_map[color])
        else:
            try:
                inferred_color = infer_color_openai(color)
                colors.append(inferred_color)
                name_to_color_map[color] = inferred_color
            except Exception as e:
                print(f"Error inferring color for product with description '{product_description}': {e}")
                return None
    return list(set(colors))


if __name__ == "__main__":
    uncategorized_products = db_functions.get_uncategorized_products_from_db(limit=10000)
    name_to_color_map = {'mint': 'green', 'anthracite': 'grey', 'safety orange': 'orange', 'rattan': 'brown', 'smoke grey': 'grey', 'grey fog': 'grey', 'heather': 'grey', 'midnight navy': 'navy', 'charcoal heather': 'grey', 'game royal': 'navy', 'team gold': 'yellow', 'dark smoke grey': 'grey', 'mineral teal': 'blue', 'light smoke grey': 'grey', 'coral chalk': 'pink', 'varsity maize': 'yellow', 'blue fury': 'blue', 'iron grey': 'grey', 'university blue': 'blue', 'sail': 'navy', 'hyper pink': 'pink', 'laser blue': 'blue', 'pure platinum': 'silver', 'wolf grey': 'grey', 'summit white': 'white', 'sanddrift': 'beige', 'action grape': 'purple', 'royal': 'blue', 'college navy': 'navy', 'carbon heather': 'grey', 'matte silver': 'silver', 'gold': 'yellow', 'light orewood brown': 'brown', 'barely green': 'green', 'total orange': 'orange', 'blackened blue': 'navy', 'rush blue': 'blue', 'pro green': 'green', 'team pewter': 'grey', 'bronze eclipse': 'brown', 'bucktan': 'brown', 'gum yellow': 'yellow', 'elemental pink': 'pink', 'pink spell': 'pink', 'team black': 'black', 'team white': 'white', 'blue void': 'blue', 'university red': 'red', 'team blue': 'blue', 'valor blue': 'blue', 'grey heather': 'grey', 'phantom heather': 'grey', 'phantom': 'multi-color', 'metallic silver': 'silver', 'armory navy': 'navy', 'vivid purple': 'purple', 'light soft pink': 'pink', 'pink oxford': 'pink', 'desert berry': 'pink', 'kelly green': 'green', 'royal blue': 'blue', 'team red': 'red', 'doll': 'pink', 'clear': 'white', 'dark beetroot': 'purple', 'particle grey': 'grey', 'citron tint': 'yellow', 'baltic blue': 'blue', 'light blue': 'blue', 'madder root': 'red', 'charcoal': 'grey', 'gunmetal': 'grey', 'mint foam': 'green', 'dark grey heather': 'grey', 'football grey': 'grey', 'fir': 'green', 'tour yellow': 'yellow', 'barely volt': 'yellow', 'volt': 'green', 'fuchsia dream': 'pink', 'vivid orange': 'orange', 'barely rose': 'pink', 'base grey': 'grey', 'metallic red bronze': 'red', 'viotech': 'purple', 'oxygen purple': 'purple', 'indigo haze': 'navy', 'lapis': 'navy', 'green spark': 'green', 'black heather': 'black', 'seal brown': 'brown', 'navy heather': 'navy', 'moss': 'green', 'amarillo': 'yellow', 'laser orange': 'orange', 'pure': 'white', 'diffused blue': 'blue', 'gym red': 'red', 'violet shock': 'purple', 'dark grey': 'grey', 'ashen slate': 'grey', 'orchid': 'purple', 'cool grey': 'grey', 'cream': 'white', 'magic ember': 'orange', 'sunset glow': 'orange', 'maroon': 'red', 'team orange': 'orange', 'field purple': 'purple', 'opti yellow': 'yellow', 'metallic copper': 'orange', 'light menta': 'green', 'dynamic turquoise': 'blue', 'fire pink': 'pink', 'tough red': 'red', 'burgundy crush': 'red', 'siren red': 'red', 'light fusion red': 'red', 'limelight': 'green', 'canyon rust': 'brown', 'topaz gold': 'yellow', 'sea coral': 'pink', 'gridiron': 'multi-color', 'bright crimson': 'red', 'obsidian': 'black', 'light iron ore': 'grey', 'light crimson': 'red', 'coconut milk': 'white', 'ironstone': 'grey', 'enamel green': 'green', 'medium silver': 'silver', 'lemon venom': 'yellow', 'dusty sage': 'green', 'diffused taupe': 'brown', 'team royal heather': 'navy', 'fossil': 'brown', 'cream ii': 'white', 'signal blue': 'blue', 'binary blue': 'blue', 'magma orange': 'orange', 'university gold': 'yellow', 'off noir': 'black', 'platinum tint': 'silver', 'cobalt bliss': 'blue', 'hot punch': 'pink', 'earth': 'brown', 'red heather': 'red', 'yellow strike': 'yellow', 'dark driftwood': 'brown', 'cardinal red': 'red', 'speed red': 'red', 'powder blue': 'blue', 'flat opal': 'white', 'off white': 'white', 'flint grey': 'grey', 'rust oxide': 'brown', 'blue lightning': 'blue', 'electric algae': 'green', 'dark teal green': 'green', 'hasta': 'multi-color', 'vapor green': 'green', 'neutral olive': 'olive', 'coast': 'blue', 'medium soft pink': 'pink', 'pale ivory': 'white', 'bio beige': 'beige', 'purple smoke': 'purple', 'ghost green': 'green', 'peach cream': 'beige', 'green abyss': 'green', 'desert ochre': 'orange', 'team royal': 'navy', 'orange trance': 'orange', 'bright mandarin': 'orange', 'olive flak': 'olive', 'court purple': 'purple', 'dark concord': 'purple', 'racer pink': 'pink', 'red clay': 'red', 'fire red': 'red', 'valerian blue': 'blue', 'light bone': 'beige', 'limestone': 'grey', 'light liquid lime': 'green', 'sequoia': 'brown', 'alligator': 'green', 'photon dust': 'multi-color', 'kelly green heather': 'green', 'light concord': 'purple', 'rough green': 'green', 'burgundy': 'red', 'green strike': 'green', 'violet ore': 'purple', 'crimson': 'red', 'dust': 'brown', 'picante red': 'red', 'blue whisper': 'blue', 'medium blue': 'blue', 'sesame': 'beige', 'cargo khaki': 'olive', 'dark turquoise': 'blue', 'atmosphere grey': 'grey', 'team crimson': 'red', 'psychic purple': 'purple', 'ghost': 'multi-color', 'dark marina blue': 'navy', 'amber': 'orange', 'pink foam': 'pink', 'mica green': 'green', 'aura': 'multi-color', 'rosewood': 'brown', 'natural': 'beige', 'medium olive': 'olive', 'pink prime': 'pink', 'khaki': 'beige', 'pink blast': 'pink', 'midwest gold': 'yellow', 'oatmeal heather': 'beige', 'chambray': 'blue', 'blustery': 'blue', 'desert orange': 'orange', 'pinksicle': 'pink', 'arctic orange': 'orange', 'lilac': 'purple', 'barely grape': 'purple', 'coastal blue': 'blue', 'varsity red': 'red', 'jetstream': 'blue', 'new orchid': 'purple', 'mystic navy': 'navy', 'taxi': 'yellow', 'cherrywood red': 'red', 'cacao wow': 'brown', 'wheat gold': 'beige', 'brilliant orange': 'orange', 'clover': 'green', 'habanero red': 'red', 'light silver': 'silver', 'ale brown': 'brown', 'carmine': 'red', 'infrared 23': 'red', 'oxen brown': 'brown', 'light aqua heather': 'blue', 'pine green': 'green', 'elemental gold': 'yellow', 'malachite': 'green', 'mean green': 'green', 'plum eclipse': 'purple', 'team maroon': 'red', 'marine': 'navy', 'ocean bliss': 'blue', 'university orange': 'orange', 'apple green': 'green', 'sky grey': 'grey', 'purple dynasty': 'purple', 'key lime': 'green', 'new emerald': 'green', 'deep royal blue': 'blue', 'washed teal': 'blue', 'coyote': 'brown', 'dark maroon': 'red', 'bright cactus': 'green', 'oil green': 'olive', 'active fuchsia': 'pink', 'spring green': 'green', 'mineral clay': 'brown', 'cosmic fuchsia': 'pink', 'hyper royal': 'blue', 'pearl white': 'white', 'desert': 'brown', 'fireberry': 'pink', 'stadium green': 'green', 'gorge green': 'green', 'canyon purple': 'purple', 'lavender mist': 'purple', 'club gold': 'yellow', 'dark ash': 'grey', 'metallic gold': 'yellow', 'light lemon twist': 'yellow', 'light sienna': 'brown', 'sport red': 'red', 'loyal blue': 'navy', 'lucky green': 'green', 'light photo blue': 'blue', 'ink': 'black', 'bright blue': 'blue', 'dark obsidian': 'navy', 'bison': 'brown', 'hyper crimson': 'red', 'green heather': 'green', 'cobblestone': 'grey', 'racer blue': 'navy', 'archaeo brown': 'brown', 'dark pony': 'black', 'hemp': 'beige', 'mantra orange': 'orange', 'neptune green': 'green', 'noise aqua': 'blue', 'gold suede': 'beige', 'mineral slate': 'grey', 'rush fuchsia': 'pink', 'kumquat': 'orange', 'dutch blue': 'navy', 'rush orange': 'orange', 'plum fog': 'purple', 'italy blue': 'navy', 'geode teal': 'multi-color', 'lemon chiffon': 'yellow', 'midnight turquoise': 'blue', 'gum light brown': 'brown', 'flat pewter': 'grey', 'parachute beige': 'beige', 'ochre': 'brown', 'deep cardinal': 'red', 'green noise': 'green', 'worn blue': 'blue', 'vivid green': 'green', 'pink bloom': 'pink', 'glacier blue': 'blue', 'light thistle': 'purple', 'lyon blue': 'navy', 'velvet brown': 'brown', 'light curry': 'yellow', 'noble red': 'red', 'active pink': 'pink', 'pumice': 'grey', 'pilgrim': 'multi-color', 'citron pulse': 'yellow', 'oracle aqua': 'blue', 'pewter': 'grey', 'chlorine blue': 'blue', 'rose whisper': 'pink', 'glacier ice': 'blue', 'chile red': 'red', 'challenge red': 'red', 'teal': 'blue', 'deep maroon': 'red', 'monarch': 'purple', 'gum medium brown': 'brown', 'pale vanilla': 'white', 'camo green': 'green', 'iced lilac': 'purple', 'palomino': 'brown', 'redstone': 'red', 'sundown': 'orange', 'noble green': 'green', 'brushed silver': 'silver', 'cave purple': 'purple', 'gum dark brown': 'brown', 'dynamic berry': 'purple', 'dark steel grey': 'grey', 'pink glaze': 'pink', 'space purple': 'purple', 'dark russet': 'brown', 'cerulean': 'blue', 'baroque brown': 'brown', 'pitch blue': 'blue', 'cone': 'multi-color', 'pistachio frost': 'green', 'old royal': 'navy', 'dynamic yellow': 'yellow', 'paramount blue': 'navy', 'light marine': 'blue', 'pearl pink': 'pink', 'moon fossil': 'grey', 'campfire orange': 'orange', 'yellow ochre': 'yellow', 'sundial': 'brown', 'oatmeal': 'beige', 'psychic blue': 'blue', 'royal pulse': 'purple', 'aluminum': 'silver', 'team bright gold': 'yellow', 'cinnabar': 'red', 'vachetta tan': 'beige', 'hunter green': 'green', 'vivid pink': 'pink', 'light steel grey': 'grey', 'scarlet': 'red', 'purple pulse': 'purple', 'true red': 'red', 'wild violet': 'purple', 'sport orange': 'orange', 'midnight fog': 'navy', 'midas gold': 'yellow', 'bordeaux': 'red', 'saturn gold': 'yellow', 'bright ceramic': 'multi-color', 'pepper red': 'red', 'gold dart': 'yellow', 'sport blue': 'blue', 'mahogany': 'brown', 'deep forest': 'green', 'metallic platinum': 'silver', 'cement grey': 'grey', 'birch heather': 'beige', 'canyon gold': 'beige', 'lemon drop': 'yellow', 'soar': 'navy', 'team scarlet': 'red', 'fossil stone': 'grey', 'fierce purple': 'purple', 'aquatone': 'blue', 'celestial gold': 'yellow', 'new green': 'green', 'pink beam': 'pink', 'light olive': 'olive', 'faded spruce': 'green', 'thunder blue': 'blue', 'team purple': 'purple', 'dynamic pink': 'pink', 'ash green': 'green', 'aviator grey': 'grey', 'ocean cube': 'blue', 'indigo storm': 'navy', 'leche blue': 'blue', 'green glow': 'green', 'green shock': 'green', 'treeline': 'green', 'bright spruce': 'green', 'gunsmoke': 'grey', 'bold berry': 'purple', 'dark atomic teal': 'navy', 'rio teal': 'blue', 'olive grey': 'olive', 'copa': 'multi-color', 'night maroon': 'purple', 'adobe': 'red', 'field silver': 'silver', 'aqua': 'blue', 'royal tint': 'blue', 'wild berry': 'pink', 'ice blue': 'blue', 'action green': 'green', 'pacific blue': 'blue', 'deep royal': 'navy', 'gym blue': 'blue', 'neutral grey': 'grey', 'vivid sky': 'blue', 'healing jade': 'green', 'yellow zest': 'yellow', 'action red': 'red', 'burnt sunrise': 'orange', 'court blue': 'navy', 'metallic dark grey': 'grey', 'metallic summit white': 'white', 'light graphite': 'grey', 'honeydew': 'green', 'scream green': 'green', 'neon yellow': 'yellow', 'bleached aqua': 'blue', 'flat silver': 'silver', 'indigo force': 'navy', 'dark blue': 'navy', 'light neutral grey': 'grey', 'truly gold': 'yellow', 'hyper orange': 'orange', 'lemon wash': 'yellow', 'wheat grass': 'green', 'barley': 'beige', 'bleached coral': 'pink', 'mystic stone': 'grey', 'celestine blue': 'blue', 'pecan': 'brown', 'brown basalt': 'brown', 'teal nebula': 'blue', 'muslin': 'multi-color', 'maroon heather': 'red', 'light bordeaux': 'red', 'french blue': 'blue', 'blue chill': 'blue', 'enigma stone': 'multi-color', 'seafoam': 'green', 'photo blue': 'blue', 'reflect silver': 'silver', 'light aqua': 'blue', 'beach': 'beige', 'chrome yellow': 'yellow', 'rush red': 'red', 'solar flare': 'orange', 'orange pearl': 'orange', 'team crimson heather': 'red', 'team blue grey': 'blue', 'electric green': 'green', 'atmosphere': 'multi-color', 'sport royal': 'navy', 'speed yellow': 'yellow', 'olive aura': 'olive', 'light army': 'olive', 'crimson pulse': 'red', 'cave stone': 'grey', 'pink gaze': 'pink', 'college grey': 'grey', 'kinetic green': 'green', 'college blue': 'navy', 'light chocolate': 'brown', 'light arctic pink': 'pink', 'boarder blue': 'blue', 'sanded gold': 'yellow', 'atomic green': 'green', 'violet frost': 'purple', 'light zitron': 'yellow', 'jade smoke': 'green', 'team orange heather': 'orange', 'concord': 'purple', 'team vegas gold': 'yellow', 'pink salt': 'pink', 'deep maroon heather': 'red', 'vast grey': 'grey', 'melon tint': 'pink', 'golden moss': 'olive', 'sport spice': 'orange', 'iron purple': 'purple', 'true blue': 'blue', 'sapphire': 'navy', 'bicoastal': 'multi-color', 'pollen': 'yellow', 'medium ash': 'grey', 'blue tint': 'blue', 'turbo green': 'green', 'tumbled grey': 'grey', 'vegas gold': 'yellow', 'wheat': 'beige', 'pomegranate': 'red', 'lobster': 'red', 'dark purple dust': 'purple', 'peach': 'pink', 'vivid sulfur': 'yellow', 'stealth': 'black', 'sport green': 'green', 'amethyst wave': 'purple', 'blue glow': 'blue', 'chutney': 'brown', 'cactus flower': 'pink', 'villain red': 'red', 'pro orange': 'orange', 'dark powder blue': 'blue', 'dark shadow': 'black', 'light green spark': 'green', 'mardi gras': 'purple', 'neptune blue': 'blue', 'rift blue': 'blue', 'neo turquoise': 'blue', 'matte aluminum': 'silver', 'cosmic bonsai': 'multi-color', 'guava ice': 'pink', 'varsity royal': 'navy', 'solar red': 'red', 'cashmere': 'beige', 'altitude green': 'green', 'watermelon': 'pink', 'sweet beet': 'purple', 'clear emerald': 'green', 'ice silver': 'silver', 'fresh water': 'blue', 'pink rise': 'pink', 'pewter grey': 'grey', 'sport gold heather': 'yellow', 'team navy': 'navy', 'alabaster': 'white', 'pro red': 'red', 'daybreak': 'pink', 'hot curry': 'orange', 'russet': 'brown', 'dark hazel': 'brown', 'igloo': 'multi-color', 'fauna brown': 'brown', 'venice': 'multi-color', 'flax': 'beige', 'light game royal heather': 'blue', 'rush blue heather': 'blue', 'metallic white': 'white', 'dark mocha': 'brown', 'infrared': 'red', 'cucumber calm': 'green', 'cyber': 'multi-color', 'blue hero': 'blue', 'forest green': 'green', 'bright citrus': 'yellow', 'dark chocolate': 'brown', 'volt glow': 'green', 'cobalt pulse': 'blue', 'jersey gold': 'yellow', 'laser pink': 'pink', 'amethyst ash': 'purple', 'light madder root': 'red', 'venom green': 'green', 'team anthracite': 'grey', 'cobalt tint': 'blue', 'blue jay': 'blue', 'ice': 'white', 'clay orange': 'orange', 'neon green': 'green', 'night silver': 'silver', 'medium grey': 'grey', 'taupe haze': 'brown', 'light armory blue': 'blue', 'rugged orange': 'orange', 'orange peel': 'orange', 'sangria': 'red', 'laser crimson': 'red', 'light dew': 'white', 'pink ice': 'pink', 'tan': 'beige', 'light grey heather': 'grey', 'brigade blue': 'navy', 'rush pink': 'pink', 'deep pewter': 'grey', 'terra brown': 'brown', 'polarized blue': 'blue', 'galactic jade': 'green', 'blue cobalt': 'blue', 'archaeo pink': 'pink', 'sport teal': 'blue', 'battle blue': 'blue', 'twine': 'brown', 'night forest': 'green', 'iris whisper': 'purple', 'dark purple': 'purple', 'team dark green': 'green', 'team brown': 'brown', 'atlantic blue heather': 'blue', 'voltage yellow': 'yellow', 'pimento': 'red', 'ice peach': 'pink', 'tourmaline': 'multi-color', 'pink glow': 'pink', 'white onyx': 'white', 'gold dust': 'yellow', 'crimson bliss': 'red', 'bleached heather': 'grey', 'global red': 'red', 'flash crimson': 'red', 'smokey mauve': 'purple', 'military blue': 'navy', 'zinnia': 'pink', 'pure violet': 'purple', 'purple dawn': 'purple', 'bright mango': 'orange', 'rose gold': 'pink', 'lemon frost': 'yellow', 'rust pink': 'pink', 'mystic hibiscus': 'pink', 'obsidian mist': 'black', 'red bark': 'red', 'clear blue': 'blue', 'hazel rush': 'brown', 'stone': 'grey', 'ghost aqua': 'blue', 'apricot agate': 'orange', 'matte olive': 'olive', 'fossil rose': 'pink', 'chambray blue': 'blue', 'particle beige': 'beige', 'dusted clay': 'brown', 'ember glow': 'orange', 'martian sunrise': 'orange', 'rave pink': 'pink', 'lime ice': 'green', 'magic flamingo': 'pink', 'deep purple': 'purple', 'oil grey': 'grey'}
    for product_info in uncategorized_products:
        inferred_colors = infer_product_color_nike_quick(product_info, name_to_color_map=name_to_color_map)
        print(f"Colors: {inferred_colors}")
        db_functions.update_product_colors(product_info["id"], inferred_colors)
    print(f"Name to color map: {name_to_color_map}")

# if __name__ == "__main__":
#     # Take in user input for the types of products that are the most important to infer
#     product_type_to_infer = input("What type of product do you want to infer for? ")
#     limit = int(input("How many products do you want to infer for? "))

#     # Get the uncategorized products
#     uncategorized_products = db_functions.get_uncategorized_products_from_db(limit=limit, bias_towards_prompt = product_type_to_infer)
#     # print("Uncategorized products: ", uncategorized_products)

#     # Infer the category for each product
#     for product in uncategorized_products:
#         # Try to infer attributes
#         try:
#             print(f"Production Description: {product['description']}")
#             inferred_attributes = infer_product_category_colors_and_gender(product)
#         except Exception as e:
#             print(f"Error inferring attributes for product {product}: {e}")
#             continue

#         # Update the product in the database
#         category = inferred_attributes["category"]
#         colors = inferred_attributes["colors"]
#         gender = inferred_attributes["gender"]
#         product_id = product["id"]
#         db_functions.update_product_category_colors_and_gender(product_id, category, colors, gender)

