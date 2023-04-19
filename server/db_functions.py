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
