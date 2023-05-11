# BEFORE RUNNING THIS SCRIPT YOU MUST
# 1) Update the product_category in get_product_details()
# 2) update gender in get_product_details
# 3) Select the right API_URL
# 5) Change the outfile name at the bottom


import json
import requests
from pprint import pprint
from http import server
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor



def get_product_details(product):
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        allowed_categories = ['top', 'bottom', 'outerwear', 'dress', 'swimwear', 'underwear', 'sleepwear', 'accessory', 'footwear']
        product_category = 'underwear' # MAKE SURE TO UPDATE THIS ON EACH RUN
        product_gender = 'men'

        product_url = "https://asos.com/us/" + product['url']
        product_price = product['price']['current']['value']
        product_name = product['name']

        response = requests.get(product_url, headers=HEADERS)
        product_soup = BeautifulSoup(response.text, 'html.parser')
        product_color = product['colour']

        product_description_div = product_soup.find('div', {'id': 'productDescriptionDetails'})
        if product_description_div:
            product_description_bullets_lis = product_description_div.find('ul').findAll('li')
            product_description = ''
            for bullet in product_description_bullets_lis:
                product_description = product_description + bullet.text + ". "
        else:
            product_description = "[No description available]"
            # num_products_description_error += 1
            # print("error finding product description. num products with description error: " + str(num_products_description_error))
        

        product_image_urls = [product['imageUrl']]
        product_image_urls.extend(product['additionalImageUrls'])
        # product_image_urls = product_soup.find('img', {'data-fade-in'="css-147n82m"}).text

        product_tags = []


        return {
            'store_name': 'asos',
            'price': product_price,
            'name': product_name,
            'raw_color': product_color,
            'description': product_description,
            'image_urls': product_image_urls,
            'tags': product_tags,
            'url': product_url,
            'category': product_category,
            'gender': product_gender
        }
    except Exception as e:
        print(f"Error processing product {product['name']}")
        return None

    
def main():
    curr_num = 0 # this is the current number of products populated on the nike page. We must iterate this in the API_URL
    
    all_product_details = []

    # num_products_description_error = 0

    num_products_processed = 0
    num_colorways_processed = 0

    # active_api = True
    while True:

        # Mens CTAS (call to actions)
        # API_URL = "https://www.asos.com/api/product/search/v2/categories/24920?offset=" + str(curr_num) + "&store=US&lang=en-US&currency=USD&country=US&keyStoreDataversion=ornjx7v-36&limit=200&region=CA"

        #Mens Hoodies and Jackets
        # API_URL = "https://www.asos.com/api/product/search/v2/categories/5668?offset=" + str(curr_num) + "&store=US&lang=en-US&currency=USD&country=US&keyStoreDataversion=ornjx7v-36&limit=200&region=CA"
        
        # Mens Accessories
        # API_URL = "https://www.asos.com/api/product/search/v2/categories/4210?offset=" + str(curr_num) + "&store=US&lang=en-US&currency=USD&country=US&keyStoreDataversion=ornjx7v-36&limit=200&region=CA"
        
        # Mens Sweaters and Cardigans
        # API_URL = "https://www.asos.com/api/product/search/v2/categories/7617?offset=" + str(curr_num) + "&store=US&lang=en-US&currency=USD&country=US&keyStoreDataversion=ornjx7v-36&limit=200&region=CA"
        
        # Mens Jewelry
        # API_URL = "https://www.asos.com/api/product/search/v2/categories/5034?offset=" + str(curr_num) + "&store=US&lang=en-US&currency=USD&country=US&keyStoreDataversion=ornjx7v-36&limit=200&region=CA"
        
        # Mens jeans
        # API_URL = "https://www.asos.com/api/product/search/v2/categories/4208?offset=" + str(curr_num) + "&store=US&lang=en-US&currency=USD&country=US&keyStoreDataversion=ornjx7v-36&limit=200&region=CA"
        
        # mens pants and chinos
        # API_URL = "https://www.asos.com/api/product/search/v2/categories/4910?offset=" + str(curr_num) + "&store=US&lang=en-US&currency=USD&country=US&keyStoreDataversion=ornjx7v-36&limit=200&region=CA"
        
        # mens underwear and socks
        API_URL = "https://www.asos.com/api/product/search/v2/categories/4030?offset=" + str(curr_num) + "&store=US&lang=en-US&currency=USD&country=US&keyStoreDataversion=ornjx7v-36&limit=200&region=CA"
        
        # Mens watches
        # API_URL = "https://www.asos.com/api/product/search/v2/categories/19855?offset=" + str(curr_num) + "&store=US&lang=en-US&currency=USD&country=US&keyStoreDataversion=ornjx7v-36&limit=200&region=CA"
        
        # Mens sunglasses
        # API_URL = "https://www.asos.com/api/product/search/v2/categories/6519?offset=" + str(curr_num) + "&store=US&lang=en-US&currency=USD&country=US&keyStoreDataversion=ornjx7v-36&limit=200&region=CA"
        
        # Mens swimsuits
        # API_URL = "https://www.asos.com/api/product/search/v2/categories/13210?offset=" + str(curr_num) + "&store=US&lang=en-US&currency=USD&country=US&keyStoreDataversion=ornjx7v-36&limit=200&region=CA"

        # mens t-shirts and tanks tops
        # API_URL = "https://www.asos.com/api/product/search/v2/categories/7616?offset=" + str(curr_num) + "&store=US&lang=en-US&currency=USD&country=US&keyStoreDataversion=ornjx7v-36&limit=200&region=CA"

        # mens shirts
        # API_URL = "https://www.asos.com/api/product/search/v2/categories/3602?offset=" + str(curr_num) + "&store=US&lang=en-US&currency=USD&country=US&keyStoreDataversion=ornjx7v-36&limit=200&region=CA"

        # mens sweatpants
        # API_URL = "https://www.asos.com/api/product/search/v2/categories/14274?offset=" + str(curr_num) + "&store=US&lang=en-US&currency=USD&country=US&keyStoreDataversion=ornjx7v-36&limit=200&region=CA"

        # Mens jackets and coats
        # API_URL = "https://www.asos.com/api/product/search/v2/categories/3606?offset=" + str(curr_num) + "&store=US&lang=en-US&currency=USD&country=US&keyStoreDataversion=ornjx7v-36&limit=200&region=CA"
        
        # mens shorts
        # API_URL = "https://www.asos.com/api/product/search/v2/categories/7078?offset=" + str(curr_num) + "&store=US&lang=en-US&currency=USD&country=US&keyStoreDataversion=ornjx7v-36&limit=200&region=CA"
        
        # mens shoes, boots, and sneakers
        # API_URL = "https://www.asos.com/api/product/search/v2/categories/4209?offset=" + str(curr_num) + "&store=US&lang=en-US&currency=USD&country=US&keyStoreDataversion=ornjx7v-36&limit=200&region=CA"
        
        
        #############################
        # UNSCRAPED ASOS PAGES #

        # Mens suits
        # https://www.asos.com/us/men/suits/cat/?cid=5678

        # mens face and body gifts
        # https://www.asos.com/us/men/face-body/50350/cat/?cid=50350

        # mens body care
        # https://www.asos.com/us/men/face-body/body-care/cat/?cid=27142

        # mens loungewear (includes pajamas i think)
        # https://www.asos.com/us/men/loungewear/cat/?cid=18797

        # mens sportswear
        # https://www.asos.com/us/men/activewear/cat/?cid=26090

        # mens CTAS
        # https://www.asos.com/us/men/ctas/cat/?cid=24920




        # Fetch data from API
        response = requests.get(API_URL)
        if response.status_code != 200:
            print(f"Error fetching data from API: {response.status_code}")
            # active_api = False # When we run out of products, this will turn false because the API_URL will be invalid
            return

        api_data = response.json()

        products = api_data['products']

        if len(products) == 0: # this will stop the loop when we run out of products
            # active_api = False
            # curr_num = curr_num + 200
            # continue
            break
        # print(len(products))

        

        # OPTIMIZED FASTER METHOD
        with ThreadPoolExecutor(max_workers=30) as executor:
        # Use executor.submit() with partial to pass multiple arguments
            futures = []
            
            for product in products:
                future = executor.submit(get_product_details, product)
                futures.append(future)
                    
            for future in futures:
                product_details = future.result()
                if product_details is not None:
                    all_product_details.append(product_details)
                    num_products_processed += 1
                    print("num products processed: " + str(num_products_processed))


        # SLOW METHOD
        # for product in products:
        #     product_details = get_product_details(product)
        #     all_product_details.append(product_details)
        #     num_products_processed +=1
        #     print(num_products_processed)


        curr_num = curr_num + 200

        # Not needed for Asos, was needed for nike
        # if curr_num > 1000: # !! MAKE SURE TO CHANGE THIS TO MATCH THE NUMBER OF PRODUCTS IN THE CATEGORY (the less dumb ways dont work)
            #  break

        # if len(all_product_details) >= 6221:
        #     break


    with open('./asos_products/mens_underwear_and_socks_asos_product_data.json', 'w') as outfile:
            json.dump(all_product_details, outfile, indent=4)

if __name__ == "__main__":
    main()
