import requests
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from supabase_py import create_client, Client



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

num_products_uploaded = 0
# url: str = "https://siosokxtbfhlkwzyvgsb.supabase.co"
# key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpb3Nva3h0YmZobGt3enl2Z3NiIiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODM5MzI5MzksImV4cCI6MTk5OTUwODkzOX0.oepDHDDYXVI0Z5i3y7wuzT-SelAlzPplX1_eIrK7vVo"
# supabase: Client = create_client(url, key)
failed_upload_products = []

def upload_product(json_object):
    # try:
    # server_url = "https://y41pim9ut5.execute-api.us-west-1.amazonaws.com/dev/insert_product_info"
    server_url = "https://mb9yaxa8o8.execute-api.us-west-1.amazonaws.com/dev/insert_product_info"
    response = requests.post(server_url, json=json_object)
    if response.status_code == 500:
        print(f"Server error for product {json_object['name']}: {response.content}")
        failed_upload_products.append(json_object)
    return response.status_code



# UPLOAD OPTION 1, STRAIGHT FORWARD
def upload_json_file(file_path):
    global num_products_uploaded
    # Load the JSON file
    with open(file_path, 'r') as json_file:
        products = json.load(json_file)
    
    for product in products:
        num_products_uploaded += 1
        status_code = upload_product(product)
        print(f"Uploaded product number {num_products_uploaded} with status code: {status_code}")
        

# FASTER OPTION 2, MUTLI THREADED, SOME REASON DIDNT WORK ON FOR TURTLESON
    # # Use ThreadPoolExecutor to handle multiple requests concurrently
    # with ThreadPoolExecutor() as executor:
    #     # Create a list to store the future results of upload_product()
    #     futures = [executor.submit(upload_product, product) for product in products]

    #     # Iterate through the results as they become available
    #     for future in as_completed(futures):
    #         status_code = future.result()
    #         num_products_uploaded += 1
    #         # print(f"Uploaded product number {num_products_uploaded} with status code: {status_code}")


def main():
    # file_path = "./asos_products/mens_underwear_and_socks_asos_product_data.json"
    # upload_json_file(file_path)

    
    folder_path = "./turtleson_products"
    
    # List all files in the directory
    files = os.listdir(folder_path)
    
    # Iterate over each file and call the upload_json_file function
    for file in files:
        # Check if it's a JSON file
        if file.endswith('.json'):
            file_path = os.path.join(folder_path, file)
            # print(f"Uploading file: {file}")
            upload_json_file(file_path)

    with open('failed_upload_temp.json', 'w') as outfile:
        json.dump(failed_upload_products, outfile, indent=4)


if __name__ == "__main__":
    main()
