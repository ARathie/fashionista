import psycopg2
import openai_utils

def get_db_connection_and_cursor():
    """Get a connection and cursor to the database."""
    connection = psycopg2.connect(user="postgres", password="jam-hackathon-project",
                                  host="db.lwaxncactpfihaqzilda.supabase.co",
                                  port="5432", database="postgres")
    # Create a cursor to perform database operations
    cursor = connection.cursor()
    return connection, cursor


def get_all_products():
    """Get all products from the database."""
    connection, cursor = get_db_connection_and_cursor()
    cursor.execute("""SELECT id, created_at, description, product_embedding, tags, name, price, url, image_urls FROM product_info""")
    products = cursor.fetchall()
    # Close communication with the database
    cursor.close()
    connection.close()
    return products


def find_similar_products(embeddable_text, num_closest_products=3):
    """Use embedding similarity search, via cosine distance, to find the most similar products"""
    # Get the embedding for the text
    embedding = openai_utils.openai_embedding(embeddable_text)

    # Get all products from the database
    all_products = get_all_products()

    # Calculate the similarities between the embedding and all products
    products_to_return = []
    for product in all_products:
        product_embedding = product[3]
        distance = openai_utils.cosine_similarity(embedding, product_embedding)
        products_to_return.append((list(product) + [distance]))
    
    # Sort the products by similarity
    products_to_return.sort(key=lambda x: x[8], reverse=True)

    # Return the top num_closest_products products
    return products_to_return[:num_closest_products]


def insert_product_info_into_db(product_info):
    """Insert product info into the database."""
    # Extract relevant info from product_info
    price = product_info["price"]
    name = product_info["name"]
    description = product_info["description"]
    image_urls = product_info["image_urls"]
    tags = product_info["tags"]
    url = product_info["url"]

    # Get the OpenAI embedding of the description + name + str(tags)
    full_product_info = f"Product Name: {name}; Description: {description}; Tags: {str(tags)}"
    embedding = openai_utils.openai_embedding(full_product_info)

    # Insert the product info into the database
    connection, cursor = get_db_connection_and_cursor()
    cursor.execute("""
        INSERT INTO product_info (price, name, description, image_urls, tags, url, product_embedding)
        VALUES (%(price)s, %(name)s, %(description)s, %(image_urls)s, %(tags)s, %(url)s, %(embedding)s)
        """, {
            "price": price,
            "name": name,
            "description": description,
            "image_urls": image_urls,
            "tags": tags,
            "url": url,
            "embedding": embedding
    })

    # Make the changes to the database persistent
    connection.commit()
    # Close communication with the database
    cursor.close()
    connection.close()


# Messaging and User Functions

def is_user_in_db(user_info):
    """Check if a user is already in the database."""
    # Extract relevant info from user_info
    email = user_info["email"]

    # Check if the user is in the database
    connection, cursor = get_db_connection_and_cursor()
    cursor.execute("""
        SELECT * FROM users
        WHERE email = %(email)s
        """, {
            "email": email
    })
    user = cursor.fetchone()
    # Close communication with the database
    cursor.close()
    connection.close()
    return user is not None


def get_user_id_from_email(email):
    """Get the user id from the email."""
    connection, cursor = get_db_connection_and_cursor()
    cursor.execute("""
        SELECT id FROM users
        WHERE email = %(email)s
        """, {
            "email": email
    })
    user_id = cursor.fetchone()[0]
    # Close communication with the database
    cursor.close()
    connection.close()
    return user_id

def insert_user_into_db(user_info):
    """Insert user info into the database, if they're not already inside the DB."""
    # Extract relevant info from user_info
    email = user_info["email"]

    if is_user_in_db(user_info):
        return

    # Insert the user info into the database
    connection, cursor = get_db_connection_and_cursor()
    cursor.execute("""
        INSERT INTO users (email)
        VALUES (%(email)s)
        """, {
            "email": email
    })

    # Make the changes to the database persistent
    connection.commit()
    # Close communication with the database
    cursor.close()
    connection.close()


def insert_message_into_db(message_info):
    """Insert message info into the database."""
    # Extract relevant info from message_info
    email = message_info["email"]
    sent_from_user = message_info["sent_from_user"]
    content = message_info["content"]
    product_ids = message_info["product_ids"]
    user_id = get_user_id_from_email(email)

    # Insert the message info into the database
    connection, cursor = get_db_connection_and_cursor()
    cursor.execute("""
        INSERT INTO messages (user_id, content, product_ids, sent_from_user)
        VALUES (%(user_id)s, %(content)s, %(product_ids)s, %(sent_from_user)s)
        """, {
            "user_id": user_id,
            "content": content,
            "product_ids": product_ids,
            "sent_from_user": sent_from_user
    })

    # Make the changes to the database persistent
    connection.commit()
    # Close communication with the database
    cursor.close()
    connection.close()


def get_all_messages_for_user(email, limit=8):
    """Get all messages for a user."""
    # Get the user id from the email
    user_id = get_user_id_from_email(email)

    # Get all messages for the user
    connection, cursor = get_db_connection_and_cursor()
    cursor.execute("""
        SELECT 
            user_id, product_ids, content, sent_from_user
        FROM messages
        WHERE user_id = %(user_id)s
        LIMIT %(limit)s
        """, {
            "user_id": user_id,
            "limit": limit
    })
    messages = cursor.fetchall()
    # Close communication with the database
    cursor.close()
    connection.close()
    output_messages = []
    for message in messages:
        output_messages.append({
            "user_id": message[0],
            "product_ids": message[1],
            "content": message[2],
            "sent_from_user": message[3]
        })
    return output_messages