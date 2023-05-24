# Fashionista GPT

## Executive Summary
Fashionista AI is building an online shopping concierge, named Fai, that assists shoppers in finding the clothes that best suit their needs through a chatbot experience. Fai will be powered by LLMs, including GPT. Shoppers can interact with the concierge in a conversational manner to curate an outfit or quickly find products. They may ask the chatbot to use context such as an event they will be attending, a vibe they want to exude, a fashion style they want to match, a celebrity’s style they want to replicate, a task they want to perform, etc. The concierge will have expert knowledge of fashion trends and styles, and be able to index all of the products offered by a particular retailer.

The chatbot will be accessed through a Google Chrome extension, in its initial version. Later on, it will be a plugin directly integrated into retailers’ websites.



## Uploading data to backend:
Follow the example inside of [server/test_upload_product.py](https://github.com/Jomanw/fashionista/blob/main/server/test_upload_product.py) in order to upload a new product to the backend - make sure all of the relevant fields are filled in, or are at least blank (like, an empty list of tags instead of just no tags). This will embed the name, description, and tags into a single embedding, so we can use it for similarity search.

The server url for uploading data is at `https://y41pim9ut5.execute-api.us-west-1.amazonaws.com/dev/insert_product_info`.


## Running the server
It's running locally for now, so just use the command `python app.py` to run in the server directory (after sourcing local venv with `source .venv/bin/activate`)

## TODO List:
- Make it use the actual backend, not the localhost
- Inserting products should also classify the following attributes:
  - category: one of ['top', 'bottom', 'outerwear', 'dress', 'swimwear', 'underwear', 'sleepwear', 'accessory', 'footwear']
  - color: one of ['red', 'green', 'blue', 'black', 'brown', 'grey', 'yellow', 'purple', 'white', 'pink', 'orange']
  - gender: one of ['men', 'women']
  - material: one of ['cotton', 'silk', 'wool', 'linen', 'polyester', 'nylon', 'rayon', 'acrylic', 'spandex', 'leather', 'knit']
- Adjust the prompt to output these categories
- Adjust the query to filter based on these categories
- Add validation to the outputs

- 

## Appendix
- "client_id": "258654283607-0m8k8l6ghs5mo0pgr6bffrhrfsm407dt.apps.googleusercontent.com",
