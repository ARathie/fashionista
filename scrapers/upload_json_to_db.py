import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed



# def process_json_object(obj):
#     # Add your custom logic to process or upload each object here
#     server_url = "https://y41pim9ut5.execute-api.us-west-1.amazonaws.com/dev/insert_product_info"
#     response = requests.post(server_url, json=obj)

# def iterate_json_file(file_path):
#     file_path = "./product_data.json"

#     with open(file_path, 'r') as json_file:
#         data = json.load(json_file)
#         if isinstance(data, list):
#             for obj in data:
#                 process_json_object(obj)
#         else:
#             print("The JSON file does not contain a list.")



import json
import requests

def upload_product(json_object):
    server_url = "https://y41pim9ut5.execute-api.us-west-1.amazonaws.com/dev/insert_product_info"
    response = requests.post(server_url, json=json_object)
    return response.status_code

def upload_json_file(file_path):
    num_products_uploaded = 0
    # Load the JSON file
    with open(file_path, 'r') as json_file:
        products = json.load(json_file)

    # Use ThreadPoolExecutor to handle multiple requests concurrently
    with ThreadPoolExecutor() as executor:
        # Create a list to store the future results of upload_product()
        futures = [executor.submit(upload_product, product) for product in products]

        # Iterate through the results as they become available
        for future in as_completed(futures):
            status_code = future.result()
            num_products_uploaded += 1
            print(f"Uploaded product number {num_products_uploaded} with status code: {status_code}")


def main():
    file_path = "./nike_products/product_data_accessories.json"
    upload_json_file(file_path)

if __name__ == "__main__":
    main()
