import constants
import os
from twilio.rest import Client

# Twilio config
# TODO: Switch these keys out
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_SID', default='ACe6264e1545ee7823bba857e7dfb47034')
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_SID', default="AC125dc512454b298c3393d7b9565aae6f") # Ash's
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH', default='7d0c2770bd63707027ed18841548ee3a')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH', default='8111651b2e54b35ae8646c930cefec82') # Ash's

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)



def send_message_twilio(to_number, from_number, message, media_url=None):
    """sends a message to a specified phone number via Twilio. It also allows for an optional media URL to be attached to the message."""
    if media_url == None:
        twilio_message = twilio_client.messages.create(
            to=to_number,
            from_=from_number,
            body=message
        )
    else:
        twilio_message = twilio_client.messages.create(
            to=to_number,
            from_=from_number,
            body=message,
            media_url=media_url
        )


def extract_message_info_from_twilio_request(request):
    """Extracts information (the message, the sender, and the receiver) from a Twilio request."""
    # keys are {'From', 'SmsMessageSid', 'FromZip', 'ToState', 'To', 'SmsSid', 'NumSegments', 'MessageSid', 'ToCountry', 'NumMedia', 'ApiVersion', 'FromCity', 'FromCountry', 'ToCity', 'ToZip', 'FromState', 'Body', 'SmsStatus', 'AccountSid'}
    message = request.values['Body']
    sender = request.values['From']
    receiver = request.values['To']
    return {'sender': sender, 'message': message, 'receiver': receiver}

def handle_twilio_webhook_request():
    print("Got a Twilio webhook request")

    # Get the message_info
    message = request.values.get('Body')
    email = request.values.get('From')
    receiver = request.values.get('To')
    if message is None:
        return jsonify(error="message field is required"), 400

    # Insert the user's message into the database
    user_message_info = {
        "email": email,
        "content": message,
        "sent_from_user": True,
        "product_ids": []
    }
    
    # If the user is a new user and we have over 100 users already, then tell them that we're not accepting new users, unless they sign up for a demo at my calendly link
    is_user_in_db = db_functions.is_user_in_db({"email": email})
    if (not is_user_in_db) and db_functions.get_num_users() > constants.MAX_NUM_USERS:
        response_message = f"Thanks for checking out Fashionista! We're oversubscribed at the moment, and we're limiting access - to start using it, please sign up for a chat at the following link: {JORDAN_CALENDLY_URL}"
        send_message_twilio(email, receiver, response_message)
        return "Too many users"


    db_functions.insert_message_into_db(user_message_info)
    
    user_messages = db_functions.get_all_messages_for_user(email, limit = 20)
    if len(user_messages) > (constants.TRIAL_MESSAGE_CUTOFF * 2): # Double this because each of their messages also results in a response message
        # We don't want to burn credits - tell people they can sign up at my calendly link for a demo, where we can do user interviews and get feedback
        response_message = f"Thanks for trying out Fashionista! If you'd like to continue using it, please sign up for a chat at the following link: {constants.JORDAN_CALENDLY_URL}"
        send_message_twilio(email, receiver, response_message)
        return "User has exceeded the trial message cutoff"

    # Use the email to get the user's previous messages, and use that to generate a response
    user_messages = db_functions.get_all_messages_for_user(email)

    # Format the messages into a format that OpenAI can understand
    messages = format_messages_with_starter_prompt(user_messages)

    # Send the messages to OpenAI to generate a response
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
    except Exception as e:
        print("Got exception: ", e)
    

    # Send the rationale back to the user
    send_message_twilio(email, receiver, rationale)

    pieces_to_return = []
    product_ids = []
    for piece_type in outfit_pieces.keys():
        # Search through the database for the products that match the outfit pieces
        outfit_piece = outfit_pieces[piece_type]
        try:
            piece_to_return = search_for_outfit_piece(outfit_piece, piece_type, rationale, num_products_to_consider=3)
            if piece_to_return is None:
                continue

            pieces_to_return.append(piece_to_return)
            product_ids.append(piece_to_return["product_id"])

            # Send the product info back to the user, as a message containing the name of the product, a link to the product, and the media_url of the product.
            # TODO: Potentially break this up into multiple messages, if the message is too long.
            product_response_message = f"Name: {piece_to_return['name']}\n\nPrice: ${piece_to_return['price']}\n\nLink: {piece_to_return['url']}"
            media_url = piece_to_return["image_urls"][0]
            # If the media_url doesn't start with "http://" or "https://", then add "https://" to the beginning of it
            if not media_url.startswith("http://") and not media_url.startswith("https://"):
                media_url = f"https://{media_url}"
            send_message_twilio(email, receiver, product_response_message, media_url=media_url)
        except Exception as e:
            print(f"Exception when searching for outfit piece: {e}")

    # Insert the response into the database
    response_info = {
        "email": email,
        "content": response,
        "sent_from_user": False,
        "product_ids": product_ids
    }
    db_functions.insert_message_into_db(response_info)

    # Send an OK response back to the server
    return str(response)