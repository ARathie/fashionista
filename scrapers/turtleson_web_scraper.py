import requests
import time
from bs4 import BeautifulSoup
import json
import math

from pprint import pprint
from http import server
from concurrent.futures import ThreadPoolExecutor

# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By



def get_product_details(product_href):
    allowed_categories = ['top', 'bottom', 'outerwear', 'dress', 'swimwear', 'underwear', 'sleepwear', 'accessory', 'footwear']
    product_url = 'https://turtleson.com' + product_href
    product_category = 'swimwear'
    product_gender = 'men'

    try:
        response = requests.get(product_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        product_name = soup.find('h1', {'class': 'product__title ff-heading fs-heading-4-base fs-heading-3-base-ns'}).text
        # product_description_div = product_soup.find('div', {'class': 'class="rte rte--product ff-body fs-body-100"'})
        # product_description = product_description_div.find('p').text

        product_description_div = soup.find('div', class_="rte rte--product ff-body fs-body-100")
        product_description = product_description_div.text.strip()
        
        tech_specs_div = soup.find('div', {'class': 'metafield-rich_text_field'})
        tech_spec_bullet_points = tech_specs_div.find_all('li')
        # Extract the text from each bullet point and concatenate
        tech_specs = ' '.join([point.text for point in tech_spec_bullet_points])
        product_description = product_description + " " + tech_specs

        # Extract product price
        price_div = soup.find('div', attrs={"class": "product__price fs-body-100"})
        price_spans = price_div.find_all('span')

        product_price = None
        for span in price_spans:
            if span.text.strip() and "$" in span.text:
                product_price = span.text.strip()
                break

        product_price = float(product_price.replace("$", "")) if product_price else None

    
        # Find all divs containing product images
        image_divs = soup.find('div', {'class': 'product__media-item'})

        # Extract image URLs from each div
        image_urls = []
        for div in image_divs:
            img_tag = div.find('img', {'class': 'image__img'})
            if img_tag and 'src' in img_tag.attrs:
                image_urls.append(img_tag['src'][2:])



        product_tags = []

        # Find the color options
        color_elements = soup.find_all('button', 
                                    {'data-option-value': True, 
                                        'class': 'product__color-swatch dynamic-variant-button'})

        # Extract the colors
        colors = [el['data-option-value'] for el in color_elements]


        # Create a product dictionary for each color
        products = []
        for color in colors:
            product = {
                'store_name': 'turtleson',
                'price': product_price,
                'name': product_name,
                'raw_color': color,  # The specific color option
                'description': product_description,
                'image_urls': image_urls,
                'tags': product_tags,
                'url': product_url,
                'category': product_category,
                'gender': product_gender
            }
            products.append(product)

        return products

    except Exception as e:
        print(f"Error processing product {product_url}")
        return []

# def scroll_to_load_products(driver, scroll_pause_time=2, max_scrolls=20):
#     body = driver.find_element(By.TAG_NAME, 'body')
#     scroll_count = 0

#     while scroll_count < max_scrolls:
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(scroll_pause_time)
#         scroll_count += 1



def main():
    # global driver
    # driver = webdriver.Chrome(ChromeDriverManager().install())
    # # driver = webdriver.Chrome('/Users/ash/Developer/projects/fashionista/chromedriver_mac64')  # Update the path to your WebDriver
    # driver.get(URL)

    # scroll_to_load_products(driver)
    
    product_data = []
    num_products = 3
    pages = math.ceil(num_products/12)
    for page in range(0,pages+1):
        # Replace 'example.com' with the URL of the clothing brand's website
        URL = 'https://turtleson.com/collections/swim-trunks' + '?page=' + str(page)
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, 'html.parser')

        products = soup.find_all('div', {'class': 'product-item__inner'})
        # products = [product_div.find('a') for product_div in product_divs]
        product_links = [product.find('a')['href'] for product in products]
        # print(product_links)

        for link in product_links:
            product_details = get_product_details(link)
            if product_details:  # Only extend if product_details is not empty
                product_data.extend(product_details)

    # driver.quit()




    with open('./turtleson_products/mens_swim_trunks_turtleson_product_data.json', 'w') as outfile:
        json.dump(product_data, outfile, indent=4)

if __name__ == "__main__":
    main()





# def get_product_details(colorway, product):

#     try:
#         product_url = "https://nike.com" + colorway['pdpUrl'][13:]

#         response = requests.get(product_url)
#         product_soup = BeautifulSoup(response.text, 'html.parser')

#         product_price = colorway['price']['currentPrice']

        
#         product_name = product['title'] + " " + product['subtitle']

        

#         product_description_div = product_soup.find('div', {'class': 'description-preview body-2 css-1pbvugb'})
#         if product_description_div:
#             product_description = colorway['colorDescription'] + ". " + product_description_div.find('p').text
#         else:
#             product_description = colorway['colorDescription'] + ". " + "[No description available]"
#             # num_products_description_error += 1
#             # print("error finding product description. num products with description error: " + str(num_products_description_error))
            
            


#         product_image_urls = [colorway['images']['portraitURL']] # only one image, try beautiful soup strategy to get more
#         # product_image_urls = product_soup.find('img', {'data-fade-in'="css-147n82m"}).text

#         product_tags = []


#         return {
#             'price': product_price,
#             'name': product_name,
#             'description': product_description,
#             'image_urls': product_image_urls,
#             'tags': product_tags,
#             'url': product_url,
#         }
#     except Exception as e:
#         print(f"Error processing product {product['title']}")
#         return None

    
# def main():
#     curr_num = 0 # this is the current number of products populated on the nike page. We must iterate this in the API_URL
#     HEADERS = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
#     }
#     all_product_details = []

#     # num_products_description_error = 0

#     num_products_processed = 0
#     num_colorways_processed = 0

#     # active_api = True
#     while True:

#         # Mens clothing
#         # API_URL = "https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=EB468EF69CDC3B9FD8289CB67CF5353D&country=us&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(US)%26filter%3Dlanguage(en)%26filter%3DemployeePrice(true)%26filter%3DattributeIds(a00f0bb2-648b-4853-9559-4cd943b7d6c6%2C0f64ecc7-d624-4e91-b171-b83a03dd8550)%26anchor%3D" + str(curr_num) + "%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D24&language=en&localizedRangeStr=%7BlowestPrice%7D%20%E2%80%94%20%7BhighestPrice%7D"
       
#         # Womens clothing
#         # API_URL = "https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=EB468EF69CDC3B9FD8289CB67CF5353D&country=us&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(US)%26filter%3Dlanguage(en)%26filter%3DemployeePrice(true)%26filter%3DattributeIds(7baf216c-acc6-4452-9e07-39c2ca77ba32%2Ca00f0bb2-648b-4853-9559-4cd943b7d6c6)%26anchor%3D" + str(curr_num) + "%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D24&language=en&localizedRangeStr=%7BlowestPrice%7D%20%E2%80%94%20%7BhighestPrice%7D"
        
#         # Mens shoes
#         # API_URL = "https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=EB468EF69CDC3B9FD8289CB67CF5353D&country=us&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(US)%26filter%3Dlanguage(en)%26filter%3DemployeePrice(true)%26filter%3DattributeIds(16633190-45e5-4830-a068-232ac7aea82c%2C0f64ecc7-d624-4e91-b171-b83a03dd8550)%26anchor%3D" + str(curr_num) + "%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D24&language=en&localizedRangeStr=%7BlowestPrice%7D%20%E2%80%94%20%7BhighestPrice%7D"
        
#         # Womens shoes
#         # API_URL = "https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=EB468EF69CDC3B9FD8289CB67CF5353D&country=us&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(US)%26filter%3Dlanguage(en)%26filter%3DemployeePrice(true)%26filter%3DattributeIds(7baf216c-acc6-4452-9e07-39c2ca77ba32%2C16633190-45e5-4830-a068-232ac7aea82c)%26anchor%3D" + str(curr_num) + "%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D24&language=en&localizedRangeStr=%7BlowestPrice%7D%20%E2%80%94%20%7BhighestPrice%7D"
        
#         # All accessories
#         API_URL = "https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=EB468EF69CDC3B9FD8289CB67CF5353D&country=us&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(US)%26filter%3Dlanguage(en)%26filter%3DemployeePrice(true)%26filter%3DattributeIds(fa863563-4508-416d-bae9-a53188c04937)%26anchor%3D" + str(curr_num) + "%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D24&language=en&localizedRangeStr=%7BlowestPrice%7D%20%E2%80%94%20%7BhighestPrice%7D"

#         # Fetch data from API
#         response = requests.get(API_URL, headers=HEADERS)
#         if response.status_code != 200:
#             print(f"Error fetching data from API: {response.status_code}")
#             # active_api = False # When we run out of products, this will turn false because the API_URL will be invalid
#             return

#         api_data = response.json()

#         data = api_data['data']


#         products_wrapper = data['products']
#         products = products_wrapper['products']
#         if not products: # must be done this way because Nike's API will sometimes return an empty response -- seemingly random
#             curr_num = curr_num + 24
#             continue
#         print(len(products))
#         temp = 0
#         for product in products:
#              for colorway in product['colorways']:
#                   temp += 1
#         print(temp)

        

#         # OPTIMIZED FASTER METHOD
#         with ThreadPoolExecutor(max_workers=30) as executor:
#         # Use executor.submit() with partial to pass multiple arguments
#             futures = []
            
#             for product in products:
#                 num_products_processed += 1
#                 print("num products processed (roughly): " + str(num_products_processed))
#                 for colorway in product['colorways']:
#                     future = executor.submit(get_product_details, colorway, product)
#                     futures.append(future)
                    
#             for future in futures:
#                 product_details = future.result()
#                 if product_details is not None:
#                     all_product_details.append(product_details)
#                     num_colorways_processed += 1
#                     print("num colorways processed: " + str(num_colorways_processed))


#         # SLOW METHOD
#         # for product in products:
#         #     for colorway in product['colorways']:
#         #         product_details = get_product_details(colorway, product)
#         #         all_product_details.append(product_details)
#         #         num_products_processed +=1
#         #         print(num_products_processed)

#         curr_num = curr_num + 24
#         if curr_num > 1000: # !! MAKE SURE TO CHANGE THIS TO MATCH THE NUMBER OF PRODUCTS IN THE CATEGORY (the less dumb ways dont work)
#              break

#         # if len(all_product_details) >= 6221:
#         #     break


#     with open('./nike_products/product_data_accessories.json', 'w') as outfile:
#             json.dump(all_product_details, outfile, indent=4)

# if __name__ == "__main__":
#     main()
