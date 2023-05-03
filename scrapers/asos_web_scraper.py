# import requests
# import time
# from bs4 import BeautifulSoup
# import json
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By

# # Replace 'example.com' with the URL of the clothing brand's website
# URL = 'https://www.nike.com/w/mens-clothing-6ymx6znik1'

# def get_product_details(product_url):
    # response = requests.get(URL)
    # soup = BeautifulSoup(response.text, 'html.parser')

    # product_name = product_soup.find('h1', {'id': 'pdp_product_title'}).text
#     product_id = product_soup.find('li', {'class': 'description-preview__style-color ncss-li'}).text
    # product_description_div = product_soup.find('div', {'class': 'description-preview body-2 css-1pbvugb'})
    # product_description = product_description_div.find('p').text

#     return {
#         'name': product_name,
#         'id': product_id,
#         'link': product_url,
#         'description': product_description
#     }

# def scroll_to_load_products(driver, scroll_pause_time=2, max_scrolls=20):
#     body = driver.find_element(By.TAG_NAME, 'body')
#     scroll_count = 0

#     while scroll_count < max_scrolls:
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(scroll_pause_time)
#         scroll_count += 1



# def main():
#     global driver
#     driver = webdriver.Chrome(ChromeDriverManager().install())
#     # driver = webdriver.Chrome('/Users/ash/Developer/projects/fashionista/chromedriver_mac64')  # Update the path to your WebDriver
#     driver.get(URL)

#     scroll_to_load_products(driver)

    # response = requests.get(URL)
    # soup = BeautifulSoup(response.text, 'html.parser')

#     products = soup.find_all('a', {'class': 'product-card__link-overlay'})
#     # products = [product_div.find('a') for product_div in product_divs]
#     product_links = [product['href'] for product in products]

#     product_data = []

#     for link in product_links:
#         product_details = get_product_details(link)
#         product_data.append(product_details)

#     driver.quit()

#     with open('product_data.json', 'w') as outfile:
#         json.dump(product_data, outfile, indent=4)

# if __name__ == "__main__":
#     main()


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
        }
    except Exception as e:
        print(f"Error processing product {product['title']}")
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
        API_URL = "https://www.asos.com/api/product/search/v2/categories/24920?offset=" + str(curr_num) + "&store=US&lang=en-US&currency=USD&country=US&keyStoreDataversion=ornjx7v-36&limit=200&region=CA"

        # Fetch data from API
        response = requests.get(API_URL)
        if response.status_code != 200:
            print(f"Error fetching data from API: {response.status_code}")
            # active_api = False # When we run out of products, this will turn false because the API_URL will be invalid
            return

        api_data = response.json()

        products = api_data['products']

        if not products: # this will stop the loop when we run out of products
            # active_api = False
            curr_num = curr_num + 200
            continue
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
        if curr_num > 0: # !! MAKE SURE TO CHANGE THIS TO MATCH THE NUMBER OF PRODUCTS IN THE CATEGORY (the less dumb ways dont work)
             break

        # if len(all_product_details) >= 6221:
        #     break


    with open('./asos_products/product_data_mens_CTAS.json', 'w') as outfile:
            json.dump(all_product_details, outfile, indent=4)

if __name__ == "__main__":
    main()
