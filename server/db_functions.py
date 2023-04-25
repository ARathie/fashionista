import psycopg2
import openai_utils
from openai_utils import openai_response
import json

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


def find_similar_products(embeddable_text, category, gender, num_closest_products=3):
    """Use embedding similarity search, via cosine distance, to find the most similar products"""
    # Get the embedding for the text
    embedding = openai_utils.openai_embedding(embeddable_text)

    # New: use pgvector to find the most similar products
    connection, cursor = get_db_connection_and_cursor()
    cursor.execute("""
        SELECT id, created_at, description, product_embedding, tags, name, price, url, image_urls, product_embedding <-> CAST(%(embedding)s AS vector) AS distance
        FROM product_info
        WHERE category = %(category)s AND (gender = %(gender)s OR gender = 'unisex')
        ORDER BY distance ASC
        LIMIT %(num_closest_products)s
        """, {
            "embedding": embedding,
            "category": category,
            "gender": gender,
            "num_closest_products": num_closest_products
        })
    
    # Get the products from the database
    products = cursor.fetchall()

    # Close communication with the database
    cursor.close()
    connection.close()

    # Return the products
    return products


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
        ORDER BY created_at DESC
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


def update_product_category_colors_and_gender(product_id, category, colors, gender):
    """Update the product category, colors, and gender"""
    # Update the product info in the database
    connection, cursor = get_db_connection_and_cursor()
    cursor.execute("""
        UPDATE product_info
        SET category = %(category)s, colors = %(colors)s, gender = %(gender)s
        WHERE id = %(product_id)s
        """, {
            "product_id": product_id,
            "category": category,
            "colors": colors,
            "gender": gender
    })

    # Make the changes to the database persistent
    connection.commit()
    # Close communication with the database
    cursor.close()
    connection.close()


def get_uncategorized_products_from_db(limit=10, bias_towards_prompt=None):
    """Pull randomly ordered products that don't have a category from the database."""
    connection, cursor = get_db_connection_and_cursor()
    if bias_towards_prompt is None:
        # In this case, we don't want to bias towards any prompt.
        cursor.execute("""
            SELECT id, name, description, tags FROM product_info
            WHERE category IS NULL
            ORDER BY RANDOM()
            LIMIT %(limit)s
            """, { "limit": limit })
    else:
        # In this case, we want to bias towards the prompt that was given.
        # Get the OpenAI embedding of the bias_towards_prompt
        bias_towards_embedding = openai_utils.openai_embedding(bias_towards_prompt)

        # Get the tags of all the products in the database, ordered by how similar they are to the bias_towards_prompt (using '<->' operator)
        cursor.execute("""
            SELECT id, name, description, tags FROM product_info
            WHERE category IS NULL
            ORDER BY product_embedding <-> CAST(%(bias_towards)s AS vector) ASC
            LIMIT %(limit)s
            """, { "limit": limit, "bias_towards": bias_towards_embedding })
        
    uncategorized_products = cursor.fetchall()
    # Close communication with the database
    cursor.close()
    connection.close()
    output_products = []
    for product in uncategorized_products:
        output_products.append({
            "id": product[0],
            "name": product[1],
            "description": product[2],
            "tags": product[3]
        })
    return output_products



